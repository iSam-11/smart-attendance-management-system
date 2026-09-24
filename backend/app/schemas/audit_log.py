from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None
    action: str
    entity_type: str
    entity_id: int | None
    old_values: str | None
    new_values: str | None
    created_at: datetime
