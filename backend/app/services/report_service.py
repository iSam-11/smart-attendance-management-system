from __future__ import annotations

from datetime import date
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.constants import ROLE_ADMIN, ROLE_FACULTY, ROLE_STUDENT
from backend.app.core.exceptions import DomainValidationError
from backend.app.repositories.faculty_assignment_repository import FacultyAssignmentRepository
from backend.app.repositories.faculty_repository import FacultyRepository
from backend.app.repositories.report_repository import ReportRepository
from backend.app.repositories.student_repository import StudentRepository
from backend.app.schemas.common import PaginatedResponse, PaginationParams
from backend.app.schemas.report import (
    LowAttendanceReportItem,
    SectionAttendanceReportItem,
    StudentAttendanceReportItem,
    SubjectAttendanceReportItem,
)


class ReportService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.report_repo = ReportRepository(db)
        self.faculty_repo = FacultyRepository(db)
        self.assignment_repo = FacultyAssignmentRepository(db)
        self.student_repo = StudentRepository(db)

    def get_student_attendance_report(
        self,
        pagination: PaginationParams,
        current_user: dict,
        student_id: int | None = None,
        subject_id: int | None = None,
        academic_term_id: int | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> PaginatedResponse[StudentAttendanceReportItem]:
        self._validate_date_range(start_date, end_date)

        role = current_user.get("role")
        user_id = int(current_user.get("sub", 0))

        allowed_assignments = None
        target_student_id = student_id

        if role == ROLE_STUDENT:
            student = self.student_repo.get_by_user_id(user_id)
            if student is None:
                return self._empty_paginated_response(pagination, StudentAttendanceReportItem)

            if student_id is not None and student_id != student.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot access attendance report for another student",
                )
            target_student_id = student.id

        elif role == ROLE_FACULTY:
            faculty = self.faculty_repo.get_by_user_id(user_id)
            if faculty is None:
                return self._empty_paginated_response(pagination, StudentAttendanceReportItem)

            my_assignments = self.assignment_repo.list(offset=0, limit=1000, faculty_id=faculty.id)
            if not my_assignments:
                return self._empty_paginated_response(pagination, StudentAttendanceReportItem)

            allowed_assignments = [(a.subject_id, a.section_id, a.academic_term_id) for a in my_assignments]

        elif role != ROLE_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        raw_rows = self.report_repo.get_enrollment_attendance_data(
            student_id=target_student_id,
            subject_id=subject_id,
            academic_term_id=academic_term_id,
            start_date=start_date,
            end_date=end_date,
            allowed_assignments=allowed_assignments,
        )

        items = []
        for r in raw_rows:
            pct = self._calculate_percentage(r["present_classes"], r["total_conducted_classes"])
            items.append(
                StudentAttendanceReportItem(
                    student_id=r["student_id"],
                    student_name=r["student_name"],
                    enrollment_number=r["enrollment_number"],
                    subject_id=r["subject_id"],
                    subject_name=r["subject_name"],
                    subject_code=r["subject_code"],
                    section_id=r["section_id"],
                    section_name=r["section_name"],
                    academic_term_id=r["academic_term_id"],
                    total_conducted_classes=r["total_conducted_classes"],
                    present_classes=r["present_classes"],
                    absent_classes=r["absent_classes"],
                    attendance_percentage=pct,
                )
            )

        paginated_items, total = self._paginate(items, pagination)
        return PaginatedResponse[StudentAttendanceReportItem](
            items=paginated_items,
            page=pagination.page,
            page_size=pagination.page_size,
            total=total,
        )

    def get_subject_attendance_report(
        self,
        pagination: PaginationParams,
        current_user: dict,
        subject_id: int | None = None,
        section_id: int | None = None,
        academic_term_id: int | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> PaginatedResponse[SubjectAttendanceReportItem]:
        self._validate_date_range(start_date, end_date)

        role = current_user.get("role")
        user_id = int(current_user.get("sub", 0))

        if role == ROLE_STUDENT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Students cannot access subject-wide attendance reports",
            )

        allowed_assignments = None

        if role == ROLE_FACULTY:
            faculty = self.faculty_repo.get_by_user_id(user_id)
            if faculty is None:
                return self._empty_paginated_response(pagination, SubjectAttendanceReportItem)

            my_assignments = self.assignment_repo.list(offset=0, limit=1000, faculty_id=faculty.id)
            if not my_assignments:
                return self._empty_paginated_response(pagination, SubjectAttendanceReportItem)

            if subject_id is not None:
                assigned_for_subj = [a for a in my_assignments if a.subject_id == subject_id]
                if not assigned_for_subj:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Faculty can access reports only for assigned subjects",
                    )

            allowed_assignments = [(a.subject_id, a.section_id, a.academic_term_id) for a in my_assignments]

        elif role != ROLE_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        raw_rows = self.report_repo.get_enrollment_attendance_data(
            subject_id=subject_id,
            section_id=section_id,
            academic_term_id=academic_term_id,
            start_date=start_date,
            end_date=end_date,
            allowed_assignments=allowed_assignments,
        )

        items = []
        for r in raw_rows:
            pct = self._calculate_percentage(r["present_classes"], r["total_conducted_classes"])
            items.append(
                SubjectAttendanceReportItem(
                    student_id=r["student_id"],
                    student_name=r["student_name"],
                    enrollment_number=r["enrollment_number"],
                    subject_id=r["subject_id"],
                    subject_name=r["subject_name"],
                    subject_code=r["subject_code"],
                    section_id=r["section_id"],
                    section_name=r["section_name"],
                    academic_term_id=r["academic_term_id"],
                    total_conducted_classes=r["total_conducted_classes"],
                    present_classes=r["present_classes"],
                    absent_classes=r["absent_classes"],
                    attendance_percentage=pct,
                )
            )

        paginated_items, total = self._paginate(items, pagination)
        return PaginatedResponse[SubjectAttendanceReportItem](
            items=paginated_items,
            page=pagination.page,
            page_size=pagination.page_size,
            total=total,
        )

    def get_section_attendance_report(
        self,
        pagination: PaginationParams,
        current_user: dict,
        section_id: int | None = None,
        academic_term_id: int | None = None,
        subject_id: int | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> PaginatedResponse[SectionAttendanceReportItem]:
        self._validate_date_range(start_date, end_date)

        role = current_user.get("role")
        user_id = int(current_user.get("sub", 0))

        if role == ROLE_STUDENT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Students cannot access section-wide attendance reports",
            )

        allowed_assignments = None

        if role == ROLE_FACULTY:
            faculty = self.faculty_repo.get_by_user_id(user_id)
            if faculty is None:
                return self._empty_paginated_response(pagination, SectionAttendanceReportItem)

            my_assignments = self.assignment_repo.list(offset=0, limit=1000, faculty_id=faculty.id)
            if not my_assignments:
                return self._empty_paginated_response(pagination, SectionAttendanceReportItem)

            if section_id is not None:
                assigned_for_sec = [a for a in my_assignments if a.section_id == section_id]
                if not assigned_for_sec:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Faculty can access reports only for assigned sections",
                    )

            allowed_assignments = [(a.subject_id, a.section_id, a.academic_term_id) for a in my_assignments]

        elif role != ROLE_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        raw_rows = self.report_repo.get_enrollment_attendance_data(
            section_id=section_id,
            academic_term_id=academic_term_id,
            subject_id=subject_id,
            start_date=start_date,
            end_date=end_date,
            allowed_assignments=allowed_assignments,
        )

        items = []
        for r in raw_rows:
            pct = self._calculate_percentage(r["present_classes"], r["total_conducted_classes"])
            items.append(
                SectionAttendanceReportItem(
                    student_id=r["student_id"],
                    student_name=r["student_name"],
                    enrollment_number=r["enrollment_number"],
                    section_id=r["section_id"],
                    section_name=r["section_name"],
                    subject_id=r["subject_id"],
                    subject_name=r["subject_name"],
                    subject_code=r["subject_code"],
                    academic_term_id=r["academic_term_id"],
                    total_conducted_classes=r["total_conducted_classes"],
                    present_classes=r["present_classes"],
                    absent_classes=r["absent_classes"],
                    attendance_percentage=pct,
                )
            )

        paginated_items, total = self._paginate(items, pagination)
        return PaginatedResponse[SectionAttendanceReportItem](
            items=paginated_items,
            page=pagination.page,
            page_size=pagination.page_size,
            total=total,
        )

    def get_low_attendance_report(
        self,
        pagination: PaginationParams,
        current_user: dict,
        threshold: float = 75.0,
        subject_id: int | None = None,
        section_id: int | None = None,
        academic_term_id: int | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> PaginatedResponse[LowAttendanceReportItem]:
        self._validate_date_range(start_date, end_date)

        role = current_user.get("role")
        user_id = int(current_user.get("sub", 0))

        if role == ROLE_STUDENT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Students cannot access low attendance reports",
            )

        allowed_assignments = None

        if role == ROLE_FACULTY:
            faculty = self.faculty_repo.get_by_user_id(user_id)
            if faculty is None:
                return self._empty_paginated_response(pagination, LowAttendanceReportItem)

            my_assignments = self.assignment_repo.list(offset=0, limit=1000, faculty_id=faculty.id)
            if not my_assignments:
                return self._empty_paginated_response(pagination, LowAttendanceReportItem)

            allowed_assignments = [(a.subject_id, a.section_id, a.academic_term_id) for a in my_assignments]

        elif role != ROLE_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        raw_rows = self.report_repo.get_enrollment_attendance_data(
            subject_id=subject_id,
            section_id=section_id,
            academic_term_id=academic_term_id,
            start_date=start_date,
            end_date=end_date,
            allowed_assignments=allowed_assignments,
        )

        items = []
        for r in raw_rows:
            pct = self._calculate_percentage(r["present_classes"], r["total_conducted_classes"])
            if pct < threshold:
                items.append(
                    LowAttendanceReportItem(
                        student_id=r["student_id"],
                        student_name=r["student_name"],
                        enrollment_number=r["enrollment_number"],
                        section_id=r["section_id"],
                        section_name=r["section_name"],
                        subject_id=r["subject_id"],
                        subject_name=r["subject_name"],
                        subject_code=r["subject_code"],
                        academic_term_id=r["academic_term_id"],
                        total_conducted_classes=r["total_conducted_classes"],
                        present_classes=r["present_classes"],
                        absent_classes=r["absent_classes"],
                        attendance_percentage=pct,
                        threshold=threshold,
                    )
                )

        paginated_items, total = self._paginate(items, pagination)
        return PaginatedResponse[LowAttendanceReportItem](
            items=paginated_items,
            page=pagination.page,
            page_size=pagination.page_size,
            total=total,
        )

    def _calculate_percentage(self, present_classes: int, total_conducted: int) -> float:
        if total_conducted == 0:
            return 0.0
        return round((present_classes / total_conducted) * 100.0, 2)

    def _validate_date_range(self, start_date: date | None, end_date: date | None) -> None:
        if start_date is not None and end_date is not None:
            if start_date > end_date:
                raise DomainValidationError("start_date cannot be later than end_date")

    def _paginate(self, items: list, pagination: PaginationParams) -> tuple[list, int]:
        total = len(items)
        offset = pagination.offset
        page_size = pagination.page_size
        paginated_items = items[offset : offset + page_size]
        return paginated_items, total

    def _empty_paginated_response(
        self, pagination: PaginationParams, item_cls: type
    ) -> PaginatedResponse:
        return PaginatedResponse(
            items=[],
            page=pagination.page,
            page_size=pagination.page_size,
            total=0,
        )
