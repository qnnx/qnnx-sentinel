from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel


class ApiSecurityEventResponse(BaseModel):
    id: UUID
    user_id: UUID | None = None
    api_key_id: UUID | None = None
    event_type: str
    endpoint: str | None = None
    method: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    details: dict[str, Any] | None = None
    created_at: datetime