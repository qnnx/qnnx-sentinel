from pydantic import BaseModel

# REQUESTS
class KeyGenRequest(BaseModel):
    algorithm: str

class SignRequest(BaseModel):
    algorithm: str
    message: str     # Plain text string
    private_key: str # Hex-encoded string

class VerifyRequest(BaseModel):
    algorithm: str
    message: str     # Plain text string
    signature: str   # Hex-encoded string
    public_key: str  # Hex-encoded string

# RESPONSES
class KeyGenResponse(BaseModel):
    public_key: str  # Hex-encoded string
    private_key: str # Hex-encoded string

class SignResponse(BaseModel):
    signature: str   # Hex-encoded string

class VerifyResponse(BaseModel):
    is_valid: bool