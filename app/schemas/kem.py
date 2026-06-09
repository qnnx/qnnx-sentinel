from pydantic import BaseModel

# REQUESTS
class KeyGenRequest(BaseModel):
    algorithm: str

class EncapsulationRequest(BaseModel):
    algorithm: str
    public_key: str  # Hex-encoded string

class DecapsulationRequest(BaseModel):
    algorithm: str
    ciphertext: str  # Hex-encoded string
    private_key: str # Hex-encoded string

# RESPONSES
class KeyGenResponse(BaseModel):
    public_key: str  # Hex-encoded string
    private_key: str # Hex-encoded string

class EncapsulationResponse(BaseModel):
    ciphertext: str    # Hex-encoded string
    shared_secret: str # Hex-encoded string

class DecapsulationResponse(BaseModel):
    shared_secret: str # Hex-encoded string