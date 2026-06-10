from fastapi import APIRouter, Depends
from app.core.dependencies import validate_api_key
from app.schemas.dsa import (
    SignRequest,
    SignResponse,
    VerifyRequest,
    VerifyResponse
)

router = APIRouter()

@router.post(
    "/sign",
    dependencies=[Depends(validate_api_key)],
    response_model=SignResponse,
    summary="Sign Message",
    description="Sign a message using a private key."
)
def sign_message(request: SignRequest):
    return SignResponse(
        signature="mock_signature_base64"
    )

@router.post(
    "/verify",
    dependencies=[Depends(validate_api_key)],
    response_model=VerifyResponse,
    summary="Verify Signature",
    description="Verify a message signature using a public key."
)
def verify_signature(request: VerifyRequest):
    return VerifyResponse(
        is_valid=True
    )
