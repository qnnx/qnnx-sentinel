import base64
import binascii

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import validate_api_key
from app.schemas.dsa import (
    SignRequest,
    SignResponse,
    VerifyRequest,
    VerifyResponse
)
from app.services import dsa_service

router = APIRouter()


def _decode_base64(value: str, field_name: str) -> bytes:
    try:
        return base64.b64decode(value, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid Base64 for {field_name}") from exc


def _encode_base64(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii")

@router.post(
    "/sign",
    dependencies=[Depends(validate_api_key)],
    response_model=SignResponse,
    summary="Sign Message",
    description="Sign a message using a private key."
)
def sign_message(request: SignRequest):
    try:
        private_key = _decode_base64(request.private_key, "private_key")
        result = dsa_service.sign_message(
            request.algorithm,
            request.message.encode("utf-8"),
            private_key,
        )
        return SignResponse(signature=_encode_base64(result["signature"]))
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Signing failed: {exc}") from exc

@router.post(
    "/verify",
    dependencies=[Depends(validate_api_key)],
    response_model=VerifyResponse,
    summary="Verify Signature",
    description="Verify a message signature using a public key."
)
def verify_signature(request: VerifyRequest):
    try:
        signature = _decode_base64(request.signature, "signature")
        public_key = _decode_base64(request.public_key, "public_key")
        result = dsa_service.verify_signature(
            request.algorithm,
            request.message.encode("utf-8"),
            signature,
            public_key,
        )
        return VerifyResponse(is_valid=result["is_valid"])
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Verification failed: {exc}") from exc
