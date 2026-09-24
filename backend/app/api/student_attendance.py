from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_pagination
from backend.app.core.constants import ROLE_ADMIN, ROLE_FACULTY, ROLE_STUDENT
from backend.app.core.dependencies import get_current_user, require_role
from backend.app.db.dependencies import get_db
from backend.app.schemas.common import PaginatedResponse, PaginationParams
from backend.app.schemas.student_attendance import (
    StudentAttendanceBulkCreate,
    StudentAttendanceRead,
)
from backend.app.services.student_attendance_service import StudentAttendanceService

router = APIRouter(prefix="/api/student-attendance", tags=["student-attendance"])


def get_student_attendance_service(
    db: Session = Depends(get_db),
) -> StudentAttendanceService:
    return StudentAttendanceService(db)


@router.post(
    "",
    response_model=list[StudentAttendanceRead],
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(ROLE_ADMIN, ROLE_FACULTY))],
)
def create_student_attendance(
    payload: StudentAttendanceBulkCreate,
    current_user: dict = Depends(get_current_user),
    service: StudentAttendanceService = Depends(get_student_attendance_service),
) -> list[StudentAttendanceRead]:
    return service.create_bulk(payload, current_user=current_user)


@router.get(
    "",
    response_model=PaginatedResponse[StudentAttendanceRead],
    dependencies=[Depends(require_role(ROLE_ADMIN, ROLE_FACULTY, ROLE_STUDENT))],
)
def list_student_attendance(
    attendance_session_id: int | None = Query(default=None),
    student_id: int | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    pagination: PaginationParams = Depends(get_pagination),
    current_user: dict = Depends(get_current_user),
    service: StudentAttendanceService = Depends(get_student_attendance_service),
) -> PaginatedResponse[StudentAttendanceRead]:
    return service.list(
        pagination,
        current_user=current_user,
        attendance_session_id=attendance_session_id,
        student_id=student_id,
        start_date=start_date,
        end_date=end_date,
        status_filter=status_filter,
    )
