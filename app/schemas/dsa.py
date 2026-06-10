from pydantic import BaseModel

# REQUESTS
class KeyGenRequest(BaseModel):
    algorithm: str

class SignRequest(BaseModel):
    algorithm: str
    message: str
    private_key: str

class VerifyRequest(BaseModel):
    algorithm: str
    message: str
    signature: str
    public_key: str

# RESPONSES
class KeyGenResponse(BaseModel):
    public_key: str
    private_key: str

class SignResponse(BaseModel):
    signature: str

class VerifyResponse(BaseModel):
    is_valid: bool