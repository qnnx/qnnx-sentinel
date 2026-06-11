from fastapi import APIRouter, Depends, HTTPException, Request

from app.core.dependencies import verify_signed_request
from app.schemas.api_key import ApiKeyContext
from app.schemas.dsa import (
    SignRequest,
    SignResponse,
    VerifyRequest,
    VerifyResponse
)
from app.services.pqc_operation_service import run_sign_operation, run_verify_operation

router = APIRouter()

@router.post(
    "/sign",
    response_model=SignResponse,
    summary="Sign Message",
    description="Sign a message using a private key."
)
def sign_message(
    request: SignRequest,
    http_request: Request,
    api_key_context: ApiKeyContext = Depends(verify_signed_request),
):
    try:
        return SignResponse(
            **run_sign_operation(
                api_key_context=api_key_context,
                algorithm=request.algorithm,
                message=request.message,
                private_key=request.private_key,
                endpoint=http_request.url.path,
                method=http_request.method,
                ip_address=http_request.client.host if http_request.client else None,
                user_agent=http_request.headers.get("user-agent"),
            )
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Signing failed: {exc}") from exc

@router.post(
    "/verify",
    response_model=VerifyResponse,
    summary="Verify Signature",
    description="Verify a message signature using a public key."
)
def verify_signature(
    request: VerifyRequest,
    http_request: Request,
    api_key_context: ApiKeyContext = Depends(verify_signed_request),
):
    try:
        return VerifyResponse(
            **run_verify_operation(
                api_key_context=api_key_context,
                algorithm=request.algorithm,
                message=request.message,
                signature=request.signature,
                public_key=request.public_key,
                endpoint=http_request.url.path,
                method=http_request.method,
                ip_address=http_request.client.host if http_request.client else None,
                user_agent=http_request.headers.get("user-agent"),
            )
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Verification failed: {exc}") from exc
