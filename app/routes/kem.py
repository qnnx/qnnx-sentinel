import base64
import binascii

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import validate_api_key
from app.schemas.kem import (
    EncapsulationRequest,
    EncapsulationResponse,
    DecapsulationRequest,
    DecapsulationResponse
)
from app.services import kem_service

router = APIRouter()


def _decode_base64(value: str, field_name: str) -> bytes:
    try:
        return base64.b64decode(value, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid Base64 for {field_name}") from exc


def _encode_base64(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii")

@router.post(
    "/kem/encapsulate",
    dependencies=[Depends(validate_api_key)],
    response_model=EncapsulationResponse,
    summary="KEM Encapsulate",
    description="Encapsulate a shared secret using a public key."
)
def kem_encapsulate(request: EncapsulationRequest):
    try:
        public_key = _decode_base64(request.public_key, "public_key")
        result = kem_service.encapsulate_secret(request.algorithm, public_key)
        return EncapsulationResponse(
            ciphertext=_encode_base64(result["ciphertext"]),
            shared_secret=_encode_base64(result["shared_secret"]),
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"KEM encapsulation failed: {exc}") from exc

@router.post(
    "/kem/decapsulate",
    dependencies=[Depends(validate_api_key)],
    response_model=DecapsulationResponse,
    summary="KEM Decapsulate",
    description="Decapsulate a shared secret using a private key."
)
def kem_decapsulate(request: DecapsulationRequest):
    try:
        ciphertext = _decode_base64(request.ciphertext, "ciphertext")
        private_key = _decode_base64(request.private_key, "private_key")
        result = kem_service.decapsulate_secret(request.algorithm, ciphertext, private_key)
        return DecapsulationResponse(
            shared_secret=_encode_base64(result["shared_secret"]),
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"KEM decapsulation failed: {exc}") from exc