from __future__ import annotations

from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.api.deps import get_pagination
from backend.app.core.constants import ROLE_ADMIN, ROLE_FACULTY, ROLE_STUDENT
from backend.app.core.dependencies import get_current_user, require_role
from backend.app.db.dependencies import get_db
from backend.app.schemas.common import PaginatedResponse, PaginationParams
from backend.app.schemas.report import (
    LowAttendanceReportItem,
    SectionAttendanceReportItem,
    StudentAttendanceReportItem,
    SubjectAttendanceReportItem,
)
from backend.app.services.report_service import ReportService

router = APIRouter(prefix="/api/reports", tags=["reports"])


def get_report_service(db: Session = Depends(get_db)) -> ReportService:
    return ReportService(db)


@router.get(
    "/student-attendance",
    response_model=PaginatedResponse[StudentAttendanceReportItem],
    dependencies=[Depends(require_role(ROLE_ADMIN, ROLE_FACULTY, ROLE_STUDENT))],
)
def get_student_attendance_report(
    student_id: int | None = Query(default=None),
    subject_id: int | None = Query(default=None),
    academic_term_id: int | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    pagination: PaginationParams = Depends(get_pagination),
    current_user: dict = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
) -> PaginatedResponse[StudentAttendanceReportItem]:
    return service.get_student_attendance_report(
        pagination,
        current_user=current_user,
        student_id=student_id,
        subject_id=subject_id,
        academic_term_id=academic_term_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get(
    "/subject-attendance",
    response_model=PaginatedResponse[SubjectAttendanceReportItem],
    dependencies=[Depends(require_role(ROLE_ADMIN, ROLE_FACULTY))],
)
def get_subject_attendance_report(
    subject_id: int | None = Query(default=None),
    section_id: int | None = Query(default=None),
    academic_term_id: int | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    pagination: PaginationParams = Depends(get_pagination),
    current_user: dict = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
) -> PaginatedResponse[SubjectAttendanceReportItem]:
    return service.get_subject_attendance_report(
        pagination,
        current_user=current_user,
        subject_id=subject_id,
        section_id=section_id,
        academic_term_id=academic_term_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get(
    "/section-attendance",
    response_model=PaginatedResponse[SectionAttendanceReportItem],
    dependencies=[Depends(require_role(ROLE_ADMIN, ROLE_FACULTY))],
)
def get_section_attendance_report(
    section_id: int | None = Query(default=None),
    academic_term_id: int | None = Query(default=None),
    subject_id: int | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    pagination: PaginationParams = Depends(get_pagination),
    current_user: dict = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
) -> PaginatedResponse[SectionAttendanceReportItem]:
    return service.get_section_attendance_report(
        pagination,
        current_user=current_user,
        section_id=section_id,
        academic_term_id=academic_term_id,
        subject_id=subject_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get(
    "/low-attendance",
    response_model=PaginatedResponse[LowAttendanceReportItem],
    dependencies=[Depends(require_role(ROLE_ADMIN, ROLE_FACULTY))],
)
def get_low_attendance_report(
    threshold: float = Query(default=75.0, ge=0.0, le=100.0),
    subject_id: int | None = Query(default=None),
    section_id: int | None = Query(default=None),
    academic_term_id: int | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    pagination: PaginationParams = Depends(get_pagination),
    current_user: dict = Depends(get_current_user),
    service: ReportService = Depends(get_report_service),
) -> PaginatedResponse[LowAttendanceReportItem]:
    return service.get_low_attendance_report(
        pagination,
        current_user=current_user,
        threshold=threshold,
        subject_id=subject_id,
        section_id=section_id,
        academic_term_id=academic_term_id,
        start_date=start_date,
        end_date=end_date,
    )
