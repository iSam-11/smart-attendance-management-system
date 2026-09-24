from __future__ import annotations

from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.api.deps import get_pagination
from backend.app.core.constants import ROLE_ADMIN, ROLE_FACULTY
from backend.app.core.dependencies import get_current_user, require_role
from backend.app.db.dependencies import get_db
from backend.app.schemas.audit_log import AuditLogRead
from backend.app.schemas.common import PaginatedResponse, PaginationParams
from backend.app.services.audit_log_service import AuditLogService

router = APIRouter(prefix="/api/audit-logs", tags=["audit-logs"])


def get_audit_log_service(db: Session = Depends(get_db)) -> AuditLogService:
    return AuditLogService(db)


@router.get(
    "",
    response_model=PaginatedResponse[AuditLogRead],
    dependencies=[Depends(require_role(ROLE_ADMIN, ROLE_FACULTY))],
)
def list_audit_logs(
    user_id: int | None = Query(default=None),
    action: str | None = Query(default=None),
    entity_type: str | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    pagination: PaginationParams = Depends(get_pagination),
    current_user: dict = Depends(get_current_user),
    service: AuditLogService = Depends(get_audit_log_service),
) -> PaginatedResponse[AuditLogRead]:
    return service.list(
        pagination,
        current_user=current_user,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        start_date=start_date,
        end_date=end_date,
    )
