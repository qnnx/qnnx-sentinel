from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ApiUsageResponse(BaseModel):
    id: UUID
    user_id: UUID | None = None
    api_key_id: UUID | None = None
    endpoint: str
    method: str
    operation: str | None = None
    algorithm: str | None = None
    response_status: int
    response_time_ms: int | None = None
    success: bool
    ip_address: str | None = None
    user_agent: str | None = None
    error_type: str | None = None
    created_at: datetime | None = None


class ApiUsageSummaryResponse(BaseModel):
    user_id: UUID
    request_count: int
    success_count: int
    failure_count: int
    success_rate: float
    endpoint_breakdown: dict[str, int]
