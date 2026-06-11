from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import verify_signed_request
from app.schemas.keygen import KeyGenRequest, KeyGenResponse
from app.services.key_service import generate_keypair

router = APIRouter()

@router.post(
    "/keygen",
    dependencies=[Depends(verify_signed_request)],
    response_model=KeyGenResponse,
    summary="Generate Key Pair",
    description="Generate a public and private key pair for a given PQC algorithm."
)
def generate_keys(request: KeyGenRequest):
    try:
        return KeyGenResponse(**generate_keypair(request.algorithm))
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Key generation failed: {exc}") from exc
