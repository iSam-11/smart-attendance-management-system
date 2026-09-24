from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_pagination
from backend.app.core.constants import ROLE_ADMIN, ROLE_FACULTY
from backend.app.core.dependencies import require_role
from backend.app.db.dependencies import get_db
from backend.app.schemas.common import PaginatedResponse, PaginationParams
from backend.app.schemas.section import SectionCreate, SectionRead, SectionUpdate
from backend.app.services.section_service import SectionService

router = APIRouter(prefix="/api/sections", tags=["sections"])


def get_section_service(db: Session = Depends(get_db)) -> SectionService:
    return SectionService(db)


@router.post(
    "",
    response_model=SectionRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(ROLE_ADMIN))],
)
def create_section(
    payload: SectionCreate,
    service: SectionService = Depends(get_section_service),
) -> SectionRead:
    return service.create(payload)


@router.get(
    "",
    response_model=PaginatedResponse[SectionRead],
    dependencies=[Depends(require_role(ROLE_ADMIN, ROLE_FACULTY))],
)
def list_sections(
    search: str | None = Query(default=None),
    program_id: int | None = Query(default=None),
    academic_term_id: int | None = Query(default=None),
    pagination: PaginationParams = Depends(get_pagination),
    service: SectionService = Depends(get_section_service),
) -> PaginatedResponse[SectionRead]:
    return service.list(
        pagination,
        search=search,
        program_id=program_id,
        academic_term_id=academic_term_id,
    )


@router.get(
    "/{section_id}",
    response_model=SectionRead,
    dependencies=[Depends(require_role(ROLE_ADMIN, ROLE_FACULTY))],
)
def get_section(
    section_id: int,
    service: SectionService = Depends(get_section_service),
) -> SectionRead:
    return service.get(section_id)


@router.put(
    "/{section_id}",
    response_model=SectionRead,
    dependencies=[Depends(require_role(ROLE_ADMIN))],
)
def update_section(
    section_id: int,
    payload: SectionUpdate,
    service: SectionService = Depends(get_section_service),
) -> SectionRead:
    return service.update(section_id, payload)


@router.delete(
    "/{section_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role(ROLE_ADMIN))],
)
def delete_section(
    section_id: int,
    service: SectionService = Depends(get_section_service),
) -> None:
    service.delete(section_id)
