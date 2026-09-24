from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_pagination
from backend.app.core.constants import ROLE_ADMIN, ROLE_FACULTY
from backend.app.core.dependencies import require_role
from backend.app.db.dependencies import get_db
from backend.app.schemas.common import PaginatedResponse, PaginationParams
from backend.app.schemas.student import StudentCreate, StudentRead, StudentUpdate
from backend.app.services.student_service import StudentService

router = APIRouter(prefix="/api/students", tags=["students"])


def get_student_service(db: Session = Depends(get_db)) -> StudentService:
    return StudentService(db)


@router.post(
    "",
    response_model=StudentRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(ROLE_ADMIN))],
)
def create_student(
    payload: StudentCreate,
    service: StudentService = Depends(get_student_service),
) -> StudentRead:
    return service.create(payload)


@router.get(
    "",
    response_model=PaginatedResponse[StudentRead],
    dependencies=[Depends(require_role(ROLE_ADMIN, ROLE_FACULTY))],
)
def list_students(
    search: str | None = Query(default=None),
    department_id: int | None = Query(default=None),
    section_id: int | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    pagination: PaginationParams = Depends(get_pagination),
    service: StudentService = Depends(get_student_service),
) -> PaginatedResponse[StudentRead]:
    return service.list(
        pagination,
        search=search,
        department_id=department_id,
        section_id=section_id,
        is_active=is_active,
    )


@router.get(
    "/{student_id}",
    response_model=StudentRead,
    dependencies=[Depends(require_role(ROLE_ADMIN, ROLE_FACULTY))],
)
def get_student(
    student_id: int,
    service: StudentService = Depends(get_student_service),
) -> StudentRead:
    return service.get(student_id)


@router.put(
    "/{student_id}",
    response_model=StudentRead,
    dependencies=[Depends(require_role(ROLE_ADMIN))],
)
def update_student(
    student_id: int,
    payload: StudentUpdate,
    service: StudentService = Depends(get_student_service),
) -> StudentRead:
    return service.update(student_id, payload)
