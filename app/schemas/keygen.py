from pydantic import BaseModel


class KeyGenRequest(BaseModel):
    algorithm: str


class KeyGenResponse(BaseModel):
    key_id: str
    algorithm: str
    key_type: str
    public_key: str
    private_key: str
    status: str
