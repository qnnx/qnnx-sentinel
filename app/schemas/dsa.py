from pydantic import BaseModel

class SignRequest(BaseModel):
    algorithm: str
    message: str
    private_key: str

class VerifyRequest(BaseModel):
    algorithm: str
    message: str
    signature: str
    public_key: str

class SignResponse(BaseModel):
    algorithm: str
    signature: str
    status: str

class VerifyResponse(BaseModel):
    algorithm: str
    is_valid: bool
    status: str
