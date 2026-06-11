from pydantic import BaseModel

class EncapsulationRequest(BaseModel):
    algorithm: str
    public_key: str

class DecapsulationRequest(BaseModel):
    algorithm: str
    ciphertext: str
    private_key: str

class EncapsulationResponse(BaseModel):
    algorithm: str
    ciphertext: str
    shared_secret: str
    status: str

class DecapsulationResponse(BaseModel):
    algorithm: str
    shared_secret: str
    status: str
