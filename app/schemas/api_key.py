from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ApiKeyResponse(BaseModel):
    id: UUID
    user_id: UUID
    key_prefix: str | None = None
    name: str | None = None
    is_active: bool
    created_at: datetime
    revoked_at: datetime | None = None


class ApiKeyContext(BaseModel):
    id: UUID
    user_id: UUID
    key_prefix: str | None = None
    name: str | None = None
    is_active: bool


class CreateApiKeyRequest(BaseModel):
    name: str


class CreateApiKeyResponse(ApiKeyResponse):
    api_key: str
    signing_secret: str


class RevokeApiKeyRequest(BaseModel):
    api_key_id: UUID