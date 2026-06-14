import logging

from fastapi import APIRouter, Depends, HTTPException, Request

# NEW: Import our settings and limiter
from app.core.config import settings
from app.core.limiter import limiter

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
logger = logging.getLogger(__name__)

@router.post(
    "/sign",
    response_model=SignResponse,
    summary="Sign Message",
    description="Sign a message using a private key."
)
@limiter.limit(settings.SIGN_RATE_LIMIT) # NEW: Apply SIGN limit (60/min)
def sign_message(
    request: Request,                   # RENAMED: from http_request to request
    payload: SignRequest,               # RENAMED: from request to payload
    api_key_context: ApiKeyContext = Depends(verify_signed_request),
):
    try:
        return SignResponse(
            **run_sign_operation(
                api_key_context=api_key_context,
                algorithm=payload.algorithm,       # UPDATED to use payload
                message=payload.message,           # UPDATED to use payload
                private_key=payload.private_key,   # UPDATED to use payload
                endpoint=request.url.path,         # UPDATED to use request
                method=request.method,             # UPDATED to use request
                ip_address=request.client.host if request.client else None, # UPDATED
                user_agent=request.headers.get("user-agent"),               # UPDATED
            )
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Signing failed")
        raise HTTPException(status_code=500, detail="Signing failed") from exc

@router.post(
    "/verify",
    response_model=VerifyResponse,
    summary="Verify Signature",
    description="Verify a message signature using a public key."
)
@limiter.limit(settings.VERIFY_RATE_LIMIT) # NEW: Apply VERIFY limit (120/min)
def verify_signature(
    request: Request,                   # RENAMED: from http_request to request
    payload: VerifyRequest,             # RENAMED: from request to payload
    api_key_context: ApiKeyContext = Depends(verify_signed_request),
):
    try:
        return VerifyResponse(
            **run_verify_operation(
                api_key_context=api_key_context,
                algorithm=payload.algorithm,       # UPDATED to use payload
                message=payload.message,           # UPDATED to use payload
                signature=payload.signature,       # UPDATED to use payload
                public_key=payload.public_key,     # UPDATED to use payload
                endpoint=request.url.path,         # UPDATED to use request
                method=request.method,             # UPDATED to use request
                ip_address=request.client.host if request.client else None, # UPDATED
                user_agent=request.headers.get("user-agent"),               # UPDATED
            )
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Verification failed")
        raise HTTPException(status_code=500, detail="Verification failed") from exc
