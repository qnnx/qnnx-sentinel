from fastapi import APIRouter, Depends
from app.core.dependencies import validate_api_key
from app.schemas.kem import (
    EncapsulationRequest,
    EncapsulationResponse,
    DecapsulationRequest,
    DecapsulationResponse
)

router = APIRouter()

@router.post(
    "/kem/encapsulate",
    dependencies=[Depends(validate_api_key)],
    response_model=EncapsulationResponse,
    summary="KEM Encapsulate",
    description="Encapsulate a shared secret using a public key."
)
def kem_encapsulate(request: EncapsulationRequest):
    return EncapsulationResponse(
        ciphertext="mock_ciphertext_base64",
        shared_secret="mock_shared_secret_base64"
    )

@router.post(
    "/kem/decapsulate",
    dependencies=[Depends(validate_api_key)],
    response_model=DecapsulationResponse,
    summary="KEM Decapsulate",
    description="Decapsulate a shared secret using a private key."
)
def kem_decapsulate(request: DecapsulationRequest):
    return DecapsulationResponse(
        shared_secret="mock_shared_secret_base64"
    )
