from fastapi import APIRouter
from app.schemas.dsa import (
    SignRequest,
    SignResponse,
    VerifyRequest,
    VerifyResponse
)

router = APIRouter()

@router.post(
    "/sign",
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
    response_model=VerifyResponse,
    summary="Verify Signature",
    description="Verify a message signature using a public key."
)
def verify_signature(request: VerifyRequest):
    return VerifyResponse(
        is_valid=True
    )