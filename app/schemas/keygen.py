from typing import Literal

from pydantic import BaseModel


class KeyGenRequest(BaseModel):
    algorithm: str
    storage_mode: Literal["customer_managed", "sentinel_managed"] = "customer_managed"


class KeyGenResponse(BaseModel):
    key_id: str
    algorithm: str
    key_type: str
    public_key: str
    private_key: str | None = None
    private_key_ref: str | None = None
    storage_mode: Literal["customer_managed", "sentinel_managed"]
    private_key_exported: bool
    status: str