from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_pagination
from backend.app.core.constants import ROLE_ADMIN, ROLE_FACULTY
from backend.app.core.dependencies import require_role
from backend.app.db.dependencies import get_db
from backend.app.schemas.common import PaginatedResponse, PaginationParams
from backend.app.schemas.faculty import FacultyCreate, FacultyRead, FacultyUpdate
from backend.app.services.faculty_service import FacultyService

router = APIRouter(prefix="/api/faculty", tags=["faculty"])


def get_faculty_service(db: Session = Depends(get_db)) -> FacultyService:
    return FacultyService(db)


@router.post(
    "",
    response_model=FacultyRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(ROLE_ADMIN))],
)
def create_faculty(
    payload: FacultyCreate,
    service: FacultyService = Depends(get_faculty_service),
) -> FacultyRead:
    return service.create(payload)


@router.get(
    "",
    response_model=PaginatedResponse[FacultyRead],
    dependencies=[Depends(require_role(ROLE_ADMIN, ROLE_FACULTY))],
)
def list_faculty(
    search: str | None = Query(default=None),
    department_id: int | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    pagination: PaginationParams = Depends(get_pagination),
    service: FacultyService = Depends(get_faculty_service),
) -> PaginatedResponse[FacultyRead]:
    return service.list(
        pagination,
        search=search,
        department_id=department_id,
        is_active=is_active,
    )


@router.get(
    "/{faculty_id}",
    response_model=FacultyRead,
    dependencies=[Depends(require_role(ROLE_ADMIN, ROLE_FACULTY))],
)
def get_faculty(
    faculty_id: int,
    service: FacultyService = Depends(get_faculty_service),
) -> FacultyRead:
    return service.get(faculty_id)


@router.put(
    "/{faculty_id}",
    response_model=FacultyRead,
    dependencies=[Depends(require_role(ROLE_ADMIN))],
)
def update_faculty(
    faculty_id: int,
    payload: FacultyUpdate,
    service: FacultyService = Depends(get_faculty_service),
) -> FacultyRead:
    return service.update(faculty_id, payload)
