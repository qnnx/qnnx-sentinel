import logging

from fastapi import APIRouter, Depends, HTTPException, Request

# NEW: Import our settings and limiter
from app.core.config import settings
from app.core.limiter import limiter

from app.core.dependencies import verify_signed_request
from app.schemas.kem import (
    EncapsulationRequest,
    EncapsulationResponse,
    DecapsulationRequest,
    DecapsulationResponse
)
from app.schemas.request_auth import RequestAuthContext
from app.services.pqc_operation_service import run_kem_decapsulation, run_kem_encapsulation

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/kem/encapsulate",
    response_model=EncapsulationResponse,
    summary="KEM Encapsulate",
    description="Encapsulate a shared secret using a public key."
)
@limiter.limit(settings.KEM_RATE_LIMIT) # NEW: Apply KEM limit
def kem_encapsulate(
    request: Request,                   # RENAMED: from http_request to request
    payload: EncapsulationRequest,      # RENAMED: from request to payload
    api_key_context: RequestAuthContext = Depends(verify_signed_request),
):
    try:
        return EncapsulationResponse(
            **run_kem_encapsulation(
                api_key_context=api_key_context,
                algorithm=payload.algorithm,       # UPDATED to use payload
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
        logger.exception("KEM encapsulation failed")
        raise HTTPException(status_code=500, detail="KEM encapsulation failed") from exc

@router.post(
    "/kem/decapsulate",
    response_model=DecapsulationResponse,
    summary="KEM Decapsulate",
    description="Decapsulate a shared secret using a private key."
)
@limiter.limit(settings.KEM_RATE_LIMIT) # NEW: Apply KEM limit
def kem_decapsulate(
    request: Request,                   # RENAMED: from http_request to request
    payload: DecapsulationRequest,      # RENAMED: from request to payload
    api_key_context: RequestAuthContext = Depends(verify_signed_request),
):
    try:
        return DecapsulationResponse(
            **run_kem_decapsulation(
                api_key_context=api_key_context,
                algorithm=payload.algorithm,       # UPDATED to use payload
                ciphertext=payload.ciphertext,     # UPDATED to use payload
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
        logger.exception("KEM decapsulation failed")
        raise HTTPException(status_code=500, detail="KEM decapsulation failed") from exc