from uuid import UUID

from pydantic import BaseModel


class RequestAuthContext(BaseModel):
    credential_id: UUID
    user_id: UUID
    key_prefix: str | None = None
    name: str | None = None
