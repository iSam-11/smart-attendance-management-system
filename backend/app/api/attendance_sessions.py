from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_pagination
from backend.app.core.constants import ROLE_ADMIN, ROLE_FACULTY
from backend.app.core.dependencies import get_current_user, require_role
from backend.app.db.dependencies import get_db
from backend.app.schemas.attendance_session import (
    AttendanceSessionCreate,
    AttendanceSessionRead,
    AttendanceSessionUpdate,
)
from backend.app.schemas.common import PaginatedResponse, PaginationParams
from backend.app.services.attendance_session_service import AttendanceSessionService

router = APIRouter(prefix="/api/attendance-sessions", tags=["attendance-sessions"])


def get_attendance_session_service(
    db: Session = Depends(get_db),
) -> AttendanceSessionService:
    return AttendanceSessionService(db)


@router.post(
    "",
    response_model=AttendanceSessionRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(ROLE_ADMIN, ROLE_FACULTY))],
)
def create_attendance_session(
    payload: AttendanceSessionCreate,
    current_user: dict = Depends(get_current_user),
    service: AttendanceSessionService = Depends(get_attendance_session_service),
) -> AttendanceSessionRead:
    return service.create(payload, current_user=current_user)


@router.get(
    "",
    response_model=PaginatedResponse[AttendanceSessionRead],
    dependencies=[Depends(require_role(ROLE_ADMIN, ROLE_FACULTY))],
)
def list_attendance_sessions(
    faculty_assignment_id: int | None = Query(default=None),
    session_date: date | None = Query(default=None),
    pagination: PaginationParams = Depends(get_pagination),
    current_user: dict = Depends(get_current_user),
    service: AttendanceSessionService = Depends(get_attendance_session_service),
) -> PaginatedResponse[AttendanceSessionRead]:
    return service.list(
        pagination,
        current_user=current_user,
        faculty_assignment_id=faculty_assignment_id,
        session_date=session_date,
    )


@router.get(
    "/{session_id}",
    response_model=AttendanceSessionRead,
    dependencies=[Depends(require_role(ROLE_ADMIN, ROLE_FACULTY))],
)
def get_attendance_session(
    session_id: int,
    current_user: dict = Depends(get_current_user),
    service: AttendanceSessionService = Depends(get_attendance_session_service),
) -> AttendanceSessionRead:
    return service.get(session_id, current_user=current_user)


@router.put(
    "/{session_id}",
    response_model=AttendanceSessionRead,
    dependencies=[Depends(require_role(ROLE_ADMIN, ROLE_FACULTY))],
)
def update_attendance_session(
    session_id: int,
    payload: AttendanceSessionUpdate,
    current_user: dict = Depends(get_current_user),
    service: AttendanceSessionService = Depends(get_attendance_session_service),
) -> AttendanceSessionRead:
    return service.update(session_id, payload, current_user=current_user)
