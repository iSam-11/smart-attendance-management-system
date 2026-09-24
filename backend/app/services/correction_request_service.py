from __future__ import annotations

from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.constants import ROLE_ADMIN, ROLE_FACULTY, ROLE_STUDENT
from backend.app.core.exceptions import ConflictError, DomainValidationError, NotFoundError
from backend.app.db.models.audit_log import AuditLog
from backend.app.db.models.correction_request import CorrectionRequest
from backend.app.repositories.attendance_session_repository import AttendanceSessionRepository
from backend.app.repositories.correction_request_repository import CorrectionRequestRepository
from backend.app.repositories.faculty_assignment_repository import FacultyAssignmentRepository
from backend.app.repositories.faculty_repository import FacultyRepository
from backend.app.repositories.student_attendance_repository import StudentAttendanceRepository
from backend.app.repositories.student_repository import StudentRepository
from backend.app.schemas.common import PaginatedResponse, PaginationParams
from backend.app.schemas.correction_request import (
    CorrectionRequestCreate,
    CorrectionRequestRead,
    CorrectionRequestReview,
)


class CorrectionRequestService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = CorrectionRequestRepository(db)
        self.student_attendance_repo = StudentAttendanceRepository(db)
        self.session_repo = AttendanceSessionRepository(db)
        self.assignment_repo = FacultyAssignmentRepository(db)
        self.faculty_repo = FacultyRepository(db)
        self.student_repo = StudentRepository(db)

    def create(
        self,
        payload: CorrectionRequestCreate,
        current_user: dict,
    ) -> CorrectionRequestRead:
        role = current_user.get("role")
        user_id = int(current_user.get("sub", 0))

        if role not in (ROLE_STUDENT, ROLE_ADMIN):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        attendance = self.student_attendance_repo.get_by_id(payload.student_attendance_id)
        if attendance is None:
            raise NotFoundError("Student attendance record not found")

        if role == ROLE_STUDENT:
            student = self.student_repo.get_by_user_id(user_id)
            if student is None or attendance.student_id != student.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot submit correction request for another student's attendance",
                )

        reason = payload.reason.strip() if payload.reason else ""
        if not reason:
            raise DomainValidationError("Correction reason must not be empty")

        valid_statuses = {"PRESENT", "ABSENT"}
        if payload.requested_status not in valid_statuses:
            raise DomainValidationError("Invalid requested status. Allowed values are PRESENT and ABSENT")

        pending = self.repository.get_pending_by_attendance_id(payload.student_attendance_id)
        if pending is not None:
            raise ConflictError("A pending correction request already exists for this attendance record")

        now = datetime.utcnow()
        request_obj = CorrectionRequest(
            student_attendance_id=payload.student_attendance_id,
            requested_by=user_id,
            requested_status=payload.requested_status,
            reason=reason,
            request_status="PENDING",
            created_at=now,
        )

        self.repository.add(request_obj)
        try:
            self.db.flush()
            audit_log = AuditLog(
                user_id=user_id,
                action="CORRECTION_REQUESTED",
                entity_type="CorrectionRequest",
                entity_id=request_obj.id,
                new_values=f"Requested status {payload.requested_status}",
                created_at=now,
            )
            self.db.add(audit_log)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        self.db.refresh(request_obj)
        return CorrectionRequestRead.model_validate(request_obj)

    def get(
        self,
        request_id: int,
        current_user: dict,
    ) -> CorrectionRequestRead:
        request_obj = self._get_or_404(request_id)
        self._authorize_access(request_obj, current_user)
        return CorrectionRequestRead.model_validate(request_obj)

    def list(
        self,
        pagination: PaginationParams,
        current_user: dict,
        student_id: int | None = None,
        student_attendance_id: int | None = None,
        request_status: str | None = None,
    ) -> PaginatedResponse[CorrectionRequestRead]:
        role = current_user.get("role")
        user_id = int(current_user.get("sub", 0))

        if role == ROLE_ADMIN:
            items = self.repository.list(
                offset=pagination.offset,
                limit=pagination.page_size,
                student_id=student_id,
                student_attendance_id=student_attendance_id,
                request_status=request_status,
            )
            total = self.repository.count(
                student_id=student_id,
                student_attendance_id=student_attendance_id,
                request_status=request_status,
            )
        elif role == ROLE_FACULTY:
            faculty = self.faculty_repo.get_by_user_id(user_id)
            if faculty is None:
                return PaginatedResponse[CorrectionRequestRead](
                    items=[], page=pagination.page, page_size=pagination.page_size, total=0
                )

            my_assignments = self.assignment_repo.list(
                offset=0, limit=1000, faculty_id=faculty.id
            )
            my_assignment_ids = [a.id for a in my_assignments]
            if not my_assignment_ids:
                return PaginatedResponse[CorrectionRequestRead](
                    items=[], page=pagination.page, page_size=pagination.page_size, total=0
                )

            items = self.repository.list(
                offset=pagination.offset,
                limit=pagination.page_size,
                student_id=student_id,
                student_attendance_id=student_attendance_id,
                request_status=request_status,
                faculty_assignment_ids=my_assignment_ids,
            )
            total = self.repository.count(
                student_id=student_id,
                student_attendance_id=student_attendance_id,
                request_status=request_status,
                faculty_assignment_ids=my_assignment_ids,
            )
        elif role == ROLE_STUDENT:
            student = self.student_repo.get_by_user_id(user_id)
            if student is None:
                return PaginatedResponse[CorrectionRequestRead](
                    items=[], page=pagination.page, page_size=pagination.page_size, total=0
                )

            if student_id is not None and student_id != student.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot view correction requests for another student",
                )

            items = self.repository.list(
                offset=pagination.offset,
                limit=pagination.page_size,
                requested_by_user_id=user_id,
                student_attendance_id=student_attendance_id,
                request_status=request_status,
            )
            total = self.repository.count(
                requested_by_user_id=user_id,
                student_attendance_id=student_attendance_id,
                request_status=request_status,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return PaginatedResponse[CorrectionRequestRead](
            items=[CorrectionRequestRead.model_validate(item) for item in items],
            page=pagination.page,
            page_size=pagination.page_size,
            total=total,
        )

    def review(
        self,
        request_id: int,
        payload: CorrectionRequestReview,
        current_user: dict,
    ) -> CorrectionRequestRead:
        request_obj = self._get_or_404(request_id)
        role = current_user.get("role")
        user_id = int(current_user.get("sub", 0))

        if role == ROLE_STUDENT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Students cannot review correction requests",
            )

        if role == ROLE_FACULTY:
            faculty = self.faculty_repo.get_by_user_id(user_id)
            attendance = self.student_attendance_repo.get_by_id(request_obj.student_attendance_id)
            session = self.session_repo.get_by_id(attendance.attendance_session_id) if attendance else None
            assignment = self.assignment_repo.get_by_id(session.faculty_assignment_id) if session else None

            if faculty is None or assignment is None or assignment.faculty_id != faculty.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Faculty cannot review correction requests for unassigned classes",
                )
        elif role != ROLE_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        if request_obj.request_status != "PENDING":
            raise DomainValidationError("Only pending requests can be reviewed")

        status_input = payload.status.upper().strip()
        if status_input in ("APPROVED", "APPROVE"):
            target_status = "APPROVED"
        elif status_input in ("REJECTED", "REJECT"):
            target_status = "REJECTED"
        else:
            raise DomainValidationError("Invalid review status. Status must be APPROVED or REJECTED")

        now = datetime.utcnow()
        request_obj.request_status = target_status
        request_obj.reviewed_by = user_id
        request_obj.reviewer_remarks = payload.reviewer_remarks
        request_obj.reviewed_at = now

        old_status = None
        if target_status == "APPROVED":
            attendance = self.student_attendance_repo.get_by_id(request_obj.student_attendance_id)
            if attendance is not None:
                old_status = attendance.status
                attendance.status = request_obj.requested_status

        action_name = "CORRECTION_APPROVED" if target_status == "APPROVED" else "CORRECTION_REJECTED"
        audit_log = AuditLog(
            user_id=user_id,
            action=action_name,
            entity_type="CorrectionRequest",
            entity_id=request_obj.id,
            old_values=f"attendance_status: {old_status}" if old_status else None,
            new_values=f"request_status: {target_status}",
            created_at=now,
        )

        try:
            self.db.add(audit_log)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

        self.db.refresh(request_obj)
        return CorrectionRequestRead.model_validate(request_obj)

    def _get_or_404(self, request_id: int) -> CorrectionRequest:
        request_obj = self.repository.get_by_id(request_id)
        if request_obj is None:
            raise NotFoundError("Correction request not found")
        return request_obj

    def _authorize_access(self, request_obj: CorrectionRequest, current_user: dict) -> None:
        role = current_user.get("role")
        user_id = int(current_user.get("sub", 0))

        if role == ROLE_ADMIN:
            return
        elif role == ROLE_STUDENT:
            if request_obj.requested_by != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot view another student's correction request",
                )
        elif role == ROLE_FACULTY:
            faculty = self.faculty_repo.get_by_user_id(user_id)
            attendance = self.student_attendance_repo.get_by_id(request_obj.student_attendance_id)
            session = self.session_repo.get_by_id(attendance.attendance_session_id) if attendance else None
            assignment = self.assignment_repo.get_by_id(session.faculty_assignment_id) if session else None

            if faculty is None or assignment is None or assignment.faculty_id != faculty.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions",
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
