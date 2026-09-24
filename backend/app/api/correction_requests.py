from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.app.api.deps import get_pagination
from backend.app.core.constants import ROLE_ADMIN, ROLE_FACULTY, ROLE_STUDENT
from backend.app.core.dependencies import get_current_user, require_role
from backend.app.db.dependencies import get_db
from backend.app.schemas.common import PaginatedResponse, PaginationParams
from backend.app.schemas.correction_request import (
    CorrectionRequestCreate,
    CorrectionRequestRead,
    CorrectionRequestReview,
)
from backend.app.services.correction_request_service import CorrectionRequestService

router = APIRouter(prefix="/api/correction-requests", tags=["correction-requests"])


def get_correction_request_service(
    db: Session = Depends(get_db),
) -> CorrectionRequestService:
    return CorrectionRequestService(db)


@router.post(
    "",
    response_model=CorrectionRequestRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(ROLE_ADMIN, ROLE_STUDENT))],
)
def create_correction_request(
    payload: CorrectionRequestCreate,
    current_user: dict = Depends(get_current_user),
    service: CorrectionRequestService = Depends(get_correction_request_service),
) -> CorrectionRequestRead:
    return service.create(payload, current_user=current_user)


@router.get(
    "",
    response_model=PaginatedResponse[CorrectionRequestRead],
    dependencies=[Depends(require_role(ROLE_ADMIN, ROLE_FACULTY, ROLE_STUDENT))],
)
def list_correction_requests(
    student_id: int | None = Query(default=None),
    student_attendance_id: int | None = Query(default=None),
    request_status: str | None = Query(default=None),
    pagination: PaginationParams = Depends(get_pagination),
    current_user: dict = Depends(get_current_user),
    service: CorrectionRequestService = Depends(get_correction_request_service),
) -> PaginatedResponse[CorrectionRequestRead]:
    return service.list(
        pagination,
        current_user=current_user,
        student_id=student_id,
        student_attendance_id=student_attendance_id,
        request_status=request_status,
    )


@router.get(
    "/{request_id}",
    response_model=CorrectionRequestRead,
    dependencies=[Depends(require_role(ROLE_ADMIN, ROLE_FACULTY, ROLE_STUDENT))],
)
def get_correction_request(
    request_id: int,
    current_user: dict = Depends(get_current_user),
    service: CorrectionRequestService = Depends(get_correction_request_service),
) -> CorrectionRequestRead:
    return service.get(request_id, current_user=current_user)


@router.post(
    "/{request_id}/review",
    response_model=CorrectionRequestRead,
    dependencies=[Depends(require_role(ROLE_ADMIN, ROLE_FACULTY))],
)
def review_correction_request_post(
    request_id: int,
    payload: CorrectionRequestReview,
    current_user: dict = Depends(get_current_user),
    service: CorrectionRequestService = Depends(get_correction_request_service),
) -> CorrectionRequestRead:
    return service.review(request_id, payload, current_user=current_user)


@router.put(
    "/{request_id}/review",
    response_model=CorrectionRequestRead,
    dependencies=[Depends(require_role(ROLE_ADMIN, ROLE_FACULTY))],
)
def review_correction_request_put(
    request_id: int,
    payload: CorrectionRequestReview,
    current_user: dict = Depends(get_current_user),
    service: CorrectionRequestService = Depends(get_correction_request_service),
) -> CorrectionRequestRead:
    return service.review(request_id, payload, current_user=current_user)
