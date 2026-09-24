from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_pagination
from backend.app.core.constants import ROLE_ADMIN, ROLE_FACULTY
from backend.app.core.dependencies import require_role
from backend.app.db.dependencies import get_db
from backend.app.schemas.common import PaginatedResponse, PaginationParams
from backend.app.schemas.department import DepartmentCreate, DepartmentRead, DepartmentUpdate
from backend.app.services.department_service import DepartmentService

router = APIRouter(prefix="/api/departments", tags=["departments"])


def get_department_service(db: Session = Depends(get_db)) -> DepartmentService:
    return DepartmentService(db)


@router.post(
    "",
    response_model=DepartmentRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(ROLE_ADMIN))],
)
def create_department(
    payload: DepartmentCreate,
    service: DepartmentService = Depends(get_department_service),
) -> DepartmentRead:
    return service.create(payload)


@router.get(
    "",
    response_model=PaginatedResponse[DepartmentRead],
    dependencies=[Depends(require_role(ROLE_ADMIN, ROLE_FACULTY))],
)
def list_departments(
    search: str | None = Query(default=None),
    pagination: PaginationParams = Depends(get_pagination),
    service: DepartmentService = Depends(get_department_service),
) -> PaginatedResponse[DepartmentRead]:
    return service.list(pagination, search=search)


@router.get(
    "/{department_id}",
    response_model=DepartmentRead,
    dependencies=[Depends(require_role(ROLE_ADMIN, ROLE_FACULTY))],
)
def get_department(
    department_id: int,
    service: DepartmentService = Depends(get_department_service),
) -> DepartmentRead:
    return service.get(department_id)


@router.put(
    "/{department_id}",
    response_model=DepartmentRead,
    dependencies=[Depends(require_role(ROLE_ADMIN))],
)
def update_department(
    department_id: int,
    payload: DepartmentUpdate,
    service: DepartmentService = Depends(get_department_service),
) -> DepartmentRead:
    return service.update(department_id, payload)


@router.delete(
    "/{department_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role(ROLE_ADMIN))],
)
def delete_department(
    department_id: int,
    service: DepartmentService = Depends(get_department_service),
) -> None:
    service.delete(department_id)
