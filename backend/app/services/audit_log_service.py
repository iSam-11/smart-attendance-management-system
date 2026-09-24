from __future__ import annotations

from datetime import date
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.core.constants import ROLE_ADMIN, ROLE_FACULTY, ROLE_STUDENT
from backend.app.core.exceptions import DomainValidationError
from backend.app.repositories.audit_log_repository import AuditLogRepository
from backend.app.schemas.audit_log import AuditLogRead
from backend.app.schemas.common import PaginatedResponse, PaginationParams


class AuditLogService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = AuditLogRepository(db)

    def list(
        self,
        pagination: PaginationParams,
        current_user: dict,
        user_id: int | None = None,
        action: str | None = None,
        entity_type: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> PaginatedResponse[AuditLogRead]:
        role = current_user.get("role")
        current_user_id = int(current_user.get("sub", 0))

        if role == ROLE_STUDENT:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Students cannot access audit logs",
            )
        elif role == ROLE_FACULTY:
            if user_id is not None and user_id != current_user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Faculty can view only their own audit logs",
                )
            target_user_id = current_user_id
        elif role == ROLE_ADMIN:
            target_user_id = user_id
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        if start_date and end_date and start_date > end_date:
            raise DomainValidationError("start_date cannot be later than end_date")

        items = self.repository.list(
            offset=pagination.offset,
            limit=pagination.page_size,
            user_id=target_user_id,
            action=action,
            entity_type=entity_type,
            start_date=start_date,
            end_date=end_date,
        )
        total = self.repository.count(
            user_id=target_user_id,
            action=action,
            entity_type=entity_type,
            start_date=start_date,
            end_date=end_date,
        )

        return PaginatedResponse[AuditLogRead](
            items=[AuditLogRead.model_validate(item) for item in items],
            page=pagination.page,
            page_size=pagination.page_size,
            total=total,
        )
