from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_pagination
from backend.app.core.constants import ROLE_ADMIN, ROLE_FACULTY
from backend.app.core.dependencies import require_role
from backend.app.db.dependencies import get_db
from backend.app.schemas.common import PaginatedResponse, PaginationParams
from backend.app.schemas.faculty_assignment import (
    FacultyAssignmentCreate,
    FacultyAssignmentRead,
    FacultyAssignmentUpdate,
)
from backend.app.services.faculty_assignment_service import FacultyAssignmentService

router = APIRouter(prefix="/api/faculty-assignments", tags=["faculty-assignments"])


def get_faculty_assignment_service(db: Session = Depends(get_db)) -> FacultyAssignmentService:
    return FacultyAssignmentService(db)


@router.post(
    "",
    response_model=FacultyAssignmentRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(ROLE_ADMIN))],
)
def create_faculty_assignment(
    payload: FacultyAssignmentCreate,
    service: FacultyAssignmentService = Depends(get_faculty_assignment_service),
) -> FacultyAssignmentRead:
    return service.create(payload)


@router.get(
    "",
    response_model=PaginatedResponse[FacultyAssignmentRead],
    dependencies=[Depends(require_role(ROLE_ADMIN, ROLE_FACULTY))],
)
def list_faculty_assignments(
    faculty_id: int | None = Query(default=None),
    subject_id: int | None = Query(default=None),
    section_id: int | None = Query(default=None),
    academic_term_id: int | None = Query(default=None),
    pagination: PaginationParams = Depends(get_pagination),
    service: FacultyAssignmentService = Depends(get_faculty_assignment_service),
) -> PaginatedResponse[FacultyAssignmentRead]:
    return service.list(
        pagination,
        faculty_id=faculty_id,
        subject_id=subject_id,
        section_id=section_id,
        academic_term_id=academic_term_id,
    )


@router.get(
    "/{assignment_id}",
    response_model=FacultyAssignmentRead,
    dependencies=[Depends(require_role(ROLE_ADMIN, ROLE_FACULTY))],
)
def get_faculty_assignment(
    assignment_id: int,
    service: FacultyAssignmentService = Depends(get_faculty_assignment_service),
) -> FacultyAssignmentRead:
    return service.get(assignment_id)


@router.put(
    "/{assignment_id}",
    response_model=FacultyAssignmentRead,
    dependencies=[Depends(require_role(ROLE_ADMIN))],
)
def update_faculty_assignment(
    assignment_id: int,
    payload: FacultyAssignmentUpdate,
    service: FacultyAssignmentService = Depends(get_faculty_assignment_service),
) -> FacultyAssignmentRead:
    return service.update(assignment_id, payload)


@router.delete(
    "/{assignment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role(ROLE_ADMIN))],
)
def delete_faculty_assignment(
    assignment_id: int,
    service: FacultyAssignmentService = Depends(get_faculty_assignment_service),
) -> None:
    service.delete(assignment_id)
