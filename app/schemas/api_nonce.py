from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ApiNonceResponse(BaseModel):
    id: UUID
    api_key_id: UUID
    nonce: str
    created_at: datetime