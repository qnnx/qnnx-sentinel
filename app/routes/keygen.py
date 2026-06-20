import logging

from fastapi import APIRouter, Depends, HTTPException, Request

# NEW: Import our settings and limiter
from app.core.config import settings
from app.core.limiter import limiter

from app.core.dependencies import verify_signed_request
from app.schemas.keygen import KeyGenRequest, KeyGenResponse
from app.schemas.request_auth import RequestAuthContext
from app.services.pqc_operation_service import generate_and_store_keypair

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/keygen",
    response_model=KeyGenResponse,
    summary="Generate Key Pair",
    description="Generate a public and private key pair for a given PQC algorithm."
)
@limiter.limit(settings.KEYGEN_RATE_LIMIT) # NEW: Apply the limit here!
def generate_keys(
    request: Request,                      # RENAMED: from http_request to request
    payload: KeyGenRequest,                # RENAMED: from request to payload
    api_key_context: RequestAuthContext = Depends(verify_signed_request),
):
    return KeyGenResponse(
        **generate_and_store_keypair(
            api_key_context=api_key_context,
            algorithm=payload.algorithm,       # UPDATED to use payload
            storage_mode=payload.storage_mode, # UPDATED to use payload
            endpoint=request.url.path,         # UPDATED to use request
            method=request.method,             # UPDATED to use request
            ip_address=request.client.host if request.client else None, # UPDATED
            user_agent=request.headers.get("user-agent"),               # UPDATED
        )
    )
