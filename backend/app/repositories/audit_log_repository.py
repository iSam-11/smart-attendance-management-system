from __future__ import annotations

from datetime import date, datetime, time
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.db.models.audit_log import AuditLog


class AuditLogRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, log: AuditLog) -> AuditLog:
        self.db.add(log)
        self.db.flush()
        return log

    def add_all(self, logs: list[AuditLog]) -> list[AuditLog]:
        self.db.add_all(logs)
        self.db.flush()
        return logs

    def list(
        self,
        *,
        offset: int,
        limit: int,
        user_id: int | None = None,
        action: str | None = None,
        entity_type: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[AuditLog]:
        stmt = select(AuditLog).order_by(AuditLog.id.desc())
        stmt = self._apply_filters(
            stmt,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            start_date=start_date,
            end_date=end_date,
        )
        return list(self.db.scalars(stmt.offset(offset).limit(limit)).all())

    def count(
        self,
        *,
        user_id: int | None = None,
        action: str | None = None,
        entity_type: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> int:
        stmt = select(func.count(AuditLog.id))
        stmt = self._apply_filters(
            stmt,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            start_date=start_date,
            end_date=end_date,
        )
        return int(self.db.scalar(stmt) or 0)

    def _apply_filters(
        self,
        stmt,
        *,
        user_id: int | None,
        action: str | None,
        entity_type: str | None,
        start_date: date | None,
        end_date: date | None,
    ):
        if user_id is not None:
            stmt = stmt.where(AuditLog.user_id == user_id)
        if action:
            stmt = stmt.where(AuditLog.action == action)
        if entity_type:
            stmt = stmt.where(AuditLog.entity_type == entity_type)
        if start_date is not None:
            stmt = stmt.where(AuditLog.created_at >= datetime.combine(start_date, time.min))
        if end_date is not None:
            stmt = stmt.where(AuditLog.created_at <= datetime.combine(end_date, time.max))
        return stmt
