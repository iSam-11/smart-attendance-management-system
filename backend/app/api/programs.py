from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_pagination
from backend.app.core.constants import ROLE_ADMIN, ROLE_FACULTY
from backend.app.core.dependencies import require_role
from backend.app.db.dependencies import get_db
from backend.app.schemas.common import PaginatedResponse, PaginationParams
from backend.app.schemas.program import ProgramCreate, ProgramRead, ProgramUpdate
from backend.app.services.program_service import ProgramService

router = APIRouter(prefix="/api/programs", tags=["programs"])


def get_program_service(db: Session = Depends(get_db)) -> ProgramService:
    return ProgramService(db)


@router.post(
    "",
    response_model=ProgramRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(ROLE_ADMIN))],
)
def create_program(
    payload: ProgramCreate,
    service: ProgramService = Depends(get_program_service),
) -> ProgramRead:
    return service.create(payload)


@router.get(
    "",
    response_model=PaginatedResponse[ProgramRead],
    dependencies=[Depends(require_role(ROLE_ADMIN, ROLE_FACULTY))],
)
def list_programs(
    search: str | None = Query(default=None),
    department_id: int | None = Query(default=None),
    pagination: PaginationParams = Depends(get_pagination),
    service: ProgramService = Depends(get_program_service),
) -> PaginatedResponse[ProgramRead]:
    return service.list(pagination, search=search, department_id=department_id)


@router.get(
    "/{program_id}",
    response_model=ProgramRead,
    dependencies=[Depends(require_role(ROLE_ADMIN, ROLE_FACULTY))],
)
def get_program(
    program_id: int,
    service: ProgramService = Depends(get_program_service),
) -> ProgramRead:
    return service.get(program_id)


@router.put(
    "/{program_id}",
    response_model=ProgramRead,
    dependencies=[Depends(require_role(ROLE_ADMIN))],
)
def update_program(
    program_id: int,
    payload: ProgramUpdate,
    service: ProgramService = Depends(get_program_service),
) -> ProgramRead:
    return service.update(program_id, payload)


@router.delete(
    "/{program_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role(ROLE_ADMIN))],
)
def delete_program(
    program_id: int,
    service: ProgramService = Depends(get_program_service),
) -> None:
    service.delete(program_id)
