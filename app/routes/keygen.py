from fastapi import APIRouter, Depends, HTTPException, Request

from app.core.dependencies import verify_signed_request
from app.schemas.api_key import ApiKeyContext
from app.schemas.keygen import KeyGenRequest, KeyGenResponse
from app.services.pqc_operation_service import generate_and_store_keypair

router = APIRouter()

@router.post(
    "/keygen",
    response_model=KeyGenResponse,
    summary="Generate Key Pair",
    description="Generate a public and private key pair for a given PQC algorithm."
)
def generate_keys(
    request: KeyGenRequest,
    http_request: Request,
    api_key_context: ApiKeyContext = Depends(verify_signed_request),
):
    try:
        return KeyGenResponse(
            **generate_and_store_keypair(
                api_key_context=api_key_context,
                algorithm=request.algorithm,
                storage_mode=request.storage_mode,
                endpoint=http_request.url.path,
                method=http_request.method,
                ip_address=http_request.client.host if http_request.client else None,
                user_agent=http_request.headers.get("user-agent"),
            )
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Key generation failed: {exc}") from exc
