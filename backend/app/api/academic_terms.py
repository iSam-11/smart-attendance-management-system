from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_pagination
from backend.app.core.constants import ROLE_ADMIN, ROLE_FACULTY
from backend.app.core.dependencies import require_role
from backend.app.db.dependencies import get_db
from backend.app.schemas.academic_term import (
    AcademicTermCreate,
    AcademicTermRead,
    AcademicTermUpdate,
)
from backend.app.schemas.common import PaginatedResponse, PaginationParams
from backend.app.services.academic_term_service import AcademicTermService

router = APIRouter(prefix="/api/academic-terms", tags=["academic-terms"])


def get_academic_term_service(db: Session = Depends(get_db)) -> AcademicTermService:
    return AcademicTermService(db)


@router.post(
    "",
    response_model=AcademicTermRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(ROLE_ADMIN))],
)
def create_academic_term(
    payload: AcademicTermCreate,
    service: AcademicTermService = Depends(get_academic_term_service),
) -> AcademicTermRead:
    return service.create(payload)


@router.get(
    "",
    response_model=PaginatedResponse[AcademicTermRead],
    dependencies=[Depends(require_role(ROLE_ADMIN, ROLE_FACULTY))],
)
def list_academic_terms(
    search: str | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    pagination: PaginationParams = Depends(get_pagination),
    service: AcademicTermService = Depends(get_academic_term_service),
) -> PaginatedResponse[AcademicTermRead]:
    return service.list(pagination, search=search, is_active=is_active)


@router.get(
    "/{term_id}",
    response_model=AcademicTermRead,
    dependencies=[Depends(require_role(ROLE_ADMIN, ROLE_FACULTY))],
)
def get_academic_term(
    term_id: int,
    service: AcademicTermService = Depends(get_academic_term_service),
) -> AcademicTermRead:
    return service.get(term_id)


@router.put(
    "/{term_id}",
    response_model=AcademicTermRead,
    dependencies=[Depends(require_role(ROLE_ADMIN))],
)
def update_academic_term(
    term_id: int,
    payload: AcademicTermUpdate,
    service: AcademicTermService = Depends(get_academic_term_service),
) -> AcademicTermRead:
    return service.update(term_id, payload)


@router.delete(
    "/{term_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role(ROLE_ADMIN))],
)
def delete_academic_term(
    term_id: int,
    service: AcademicTermService = Depends(get_academic_term_service),
) -> None:
    service.delete(term_id)
