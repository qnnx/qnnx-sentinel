from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class KeyGenRequest(BaseModel):
    algorithm: str

class KeyGenResponse(BaseModel):
    algorithm: str
    public_key: str
    private_key: str

@router.post(
    "/keygen",
    response_model=KeyGenResponse,
    summary="Generate Key Pair",
    description="Generate a public and private key pair for a given PQC algorithm."
)
def generate_keys(request: KeyGenRequest):
    return KeyGenResponse(
        algorithm=request.algorithm,
        public_key="mock_public_key_base64",
        private_key="mock_private_key_base64"
    )