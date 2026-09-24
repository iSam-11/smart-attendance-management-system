from __future__ import annotations

from datetime import date, datetime
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.core.constants import ROLE_ADMIN, ROLE_FACULTY, ROLE_STUDENT
from backend.app.core.exceptions import ConflictError, DomainValidationError, NotFoundError
from backend.app.db.models.audit_log import AuditLog
from backend.app.db.models.student_attendance import StudentAttendance
from backend.app.repositories.attendance_session_repository import AttendanceSessionRepository
from backend.app.repositories.faculty_assignment_repository import FacultyAssignmentRepository
from backend.app.repositories.faculty_repository import FacultyRepository
from backend.app.repositories.student_attendance_repository import StudentAttendanceRepository
from backend.app.repositories.student_enrollment_repository import StudentEnrollmentRepository
from backend.app.repositories.student_repository import StudentRepository
from backend.app.schemas.common import PaginatedResponse, PaginationParams
from backend.app.schemas.student_attendance import (
    StudentAttendanceBulkCreate,
    StudentAttendanceRead,
)


class StudentAttendanceService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.student_attendance_repo = StudentAttendanceRepository(db)
        self.session_repo = AttendanceSessionRepository(db)
        self.assignment_repo = FacultyAssignmentRepository(db)
        self.faculty_repo = FacultyRepository(db)
        self.student_repo = StudentRepository(db)
        self.enrollment_repo = StudentEnrollmentRepository(db)

    def create_bulk(
        self,
        payload: StudentAttendanceBulkCreate,
        current_user: dict,
    ) -> list[StudentAttendanceRead]:
        role = current_user.get("role")
        user_id = int(current_user.get("sub", 0))

        session = self.session_repo.get_by_id(payload.attendance_session_id)
        if session is None:
            raise NotFoundError("Attendance session not found")

        assignment = self.assignment_repo.get_by_id(session.faculty_assignment_id)
        if assignment is None:
            raise NotFoundError("Faculty assignment not found for this session")

        if role == ROLE_FACULTY:
            faculty = self.faculty_repo.get_by_user_id(user_id)
            if faculty is None or assignment.faculty_id != faculty.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Faculty cannot mark attendance for another faculty's session",
                )
        elif role != ROLE_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        student_ids = [entry.student_id for entry in payload.entries]
        if len(student_ids) != len(set(student_ids)):
            raise DomainValidationError("Duplicate student entries in attendance submission")

        valid_statuses = {"PRESENT", "ABSENT"}

        for entry in payload.entries:
            if entry.status not in valid_statuses:
                raise DomainValidationError("Invalid status. Status must be PRESENT or ABSENT")

            student = self.student_repo.get_by_id(entry.student_id)
            if student is None:
                raise NotFoundError(f"Student not found with ID {entry.student_id}")
            if not student.is_active:
                raise DomainValidationError(f"Student with ID {entry.student_id} is not active")

            enrollment = self.enrollment_repo.get_by_unique_composite(
                student_id=entry.student_id,
                subject_id=assignment.subject_id,
                section_id=assignment.section_id,
                academic_term_id=assignment.academic_term_id,
            )
            if enrollment is None:
                raise DomainValidationError(
                    f"Student with ID {entry.student_id} is not enrolled in this session's subject, section, and academic term"
                )

            existing = self.student_attendance_repo.get_by_session_and_student(
                payload.attendance_session_id,
                entry.student_id,
            )
            if existing is not None:
                raise ConflictError(
                    f"Attendance record already exists for student ID {entry.student_id} in this session"
                )

        records = []
        now = datetime.utcnow()
        for entry in payload.entries:
            records.append(
                StudentAttendance(
                    attendance_session_id=payload.attendance_session_id,
                    student_id=entry.student_id,
                    status=entry.status,
                    remarks=entry.remarks,
                    marked_at=now,
                )
            )

        audit_log = AuditLog(
            user_id=user_id,
            action="ATTENDANCE_MARKED",
            entity_type="AttendanceSession",
            entity_id=payload.attendance_session_id,
            new_values=f"Marked {len(records)} students for session {payload.attendance_session_id}",
            created_at=now,
        )

        try:
            self.student_attendance_repo.add_all(records)
            self.db.add(audit_log)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise ConflictError("Attendance record already exists for one or more students in this session")
        except Exception:
            self.db.rollback()
            raise

        for record in records:
            self.db.refresh(record)

        return [StudentAttendanceRead.model_validate(record) for record in records]

    def list(
        self,
        pagination: PaginationParams,
        current_user: dict,
        attendance_session_id: int | None = None,
        student_id: int | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        status_filter: str | None = None,
    ) -> PaginatedResponse[StudentAttendanceRead]:
        role = current_user.get("role")
        user_id = int(current_user.get("sub", 0))

        if role == ROLE_ADMIN:
            items = self.student_attendance_repo.list(
                offset=pagination.offset,
                limit=pagination.page_size,
                attendance_session_id=attendance_session_id,
                student_id=student_id,
                start_date=start_date,
                end_date=end_date,
                status=status_filter,
            )
            total = self.student_attendance_repo.count(
                attendance_session_id=attendance_session_id,
                student_id=student_id,
                start_date=start_date,
                end_date=end_date,
                status=status_filter,
            )
        elif role == ROLE_FACULTY:
            faculty = self.faculty_repo.get_by_user_id(user_id)
            if faculty is None:
                return PaginatedResponse[StudentAttendanceRead](
                    items=[], page=pagination.page, page_size=pagination.page_size, total=0
                )

            my_assignments = self.assignment_repo.list(
                offset=0, limit=1000, faculty_id=faculty.id
            )
            my_assignment_ids = [a.id for a in my_assignments]
            if not my_assignment_ids:
                return PaginatedResponse[StudentAttendanceRead](
                    items=[], page=pagination.page, page_size=pagination.page_size, total=0
                )

            my_sessions = self.session_repo.list(
                offset=0, limit=10000, faculty_assignment_ids=my_assignment_ids
            )
            my_session_ids = [s.id for s in my_sessions]

            if attendance_session_id is not None:
                if attendance_session_id not in my_session_ids:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Insufficient permissions",
                    )
                target_session_ids = [attendance_session_id]
            else:
                target_session_ids = my_session_ids

            if not target_session_ids:
                return PaginatedResponse[StudentAttendanceRead](
                    items=[], page=pagination.page, page_size=pagination.page_size, total=0
                )

            items = self.student_attendance_repo.list(
                offset=pagination.offset,
                limit=pagination.page_size,
                attendance_session_id=None if attendance_session_id is not None else None,
                student_id=student_id,
                start_date=start_date,
                end_date=end_date,
                status=status_filter,
                session_ids=target_session_ids,
            )
            total = self.student_attendance_repo.count(
                attendance_session_id=None if attendance_session_id is not None else None,
                student_id=student_id,
                start_date=start_date,
                end_date=end_date,
                status=status_filter,
                session_ids=target_session_ids,
            )
        elif role == ROLE_STUDENT:
            student = self.student_repo.get_by_user_id(user_id)
            if student is None:
                return PaginatedResponse[StudentAttendanceRead](
                    items=[], page=pagination.page, page_size=pagination.page_size, total=0
                )

            if student_id is not None and student_id != student.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot view attendance records for another student",
                )

            items = self.student_attendance_repo.list(
                offset=pagination.offset,
                limit=pagination.page_size,
                attendance_session_id=attendance_session_id,
                student_id=student.id,
                start_date=start_date,
                end_date=end_date,
                status=status_filter,
            )
            total = self.student_attendance_repo.count(
                attendance_session_id=attendance_session_id,
                student_id=student.id,
                start_date=start_date,
                end_date=end_date,
                status=status_filter,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return PaginatedResponse[StudentAttendanceRead](
            items=[StudentAttendanceRead.model_validate(item) for item in items],
            page=pagination.page,
            page_size=pagination.page_size,
            total=total,
        )
