from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_pagination
from backend.app.core.constants import ROLE_ADMIN, ROLE_FACULTY
from backend.app.core.dependencies import require_role
from backend.app.db.dependencies import get_db
from backend.app.schemas.common import PaginatedResponse, PaginationParams
from backend.app.schemas.subject import SubjectCreate, SubjectRead, SubjectUpdate
from backend.app.services.subject_service import SubjectService

router = APIRouter(prefix="/api/subjects", tags=["subjects"])


def get_subject_service(db: Session = Depends(get_db)) -> SubjectService:
    return SubjectService(db)


@router.post(
    "",
    response_model=SubjectRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(ROLE_ADMIN))],
)
def create_subject(
    payload: SubjectCreate,
    service: SubjectService = Depends(get_subject_service),
) -> SubjectRead:
    return service.create(payload)


@router.get(
    "",
    response_model=PaginatedResponse[SubjectRead],
    dependencies=[Depends(require_role(ROLE_ADMIN, ROLE_FACULTY))],
)
def list_subjects(
    search: str | None = Query(default=None),
    department_id: int | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    pagination: PaginationParams = Depends(get_pagination),
    service: SubjectService = Depends(get_subject_service),
) -> PaginatedResponse[SubjectRead]:
    return service.list(
        pagination,
        search=search,
        department_id=department_id,
        is_active=is_active,
    )


@router.get(
    "/{subject_id}",
    response_model=SubjectRead,
    dependencies=[Depends(require_role(ROLE_ADMIN, ROLE_FACULTY))],
)
def get_subject(
    subject_id: int,
    service: SubjectService = Depends(get_subject_service),
) -> SubjectRead:
    return service.get(subject_id)


@router.put(
    "/{subject_id}",
    response_model=SubjectRead,
    dependencies=[Depends(require_role(ROLE_ADMIN))],
)
def update_subject(
    subject_id: int,
    payload: SubjectUpdate,
    service: SubjectService = Depends(get_subject_service),
) -> SubjectRead:
    return service.update(subject_id, payload)


@router.delete(
    "/{subject_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_role(ROLE_ADMIN))],
)
def delete_subject(
    subject_id: int,
    service: SubjectService = Depends(get_subject_service),
) -> None:
    service.delete(subject_id)
