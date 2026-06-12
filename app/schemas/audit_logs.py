from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: UUID
    event_type: str
    resource_type: str | None = None
    resource_id: str | None = None
    status: str | None = None
    user_id: UUID | None = None
    api_key_id: UUID | None = None
    ip_address: str | None = None
    details: dict[str, Any] | None = None
    created_at: datetime