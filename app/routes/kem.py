from fastapi import APIRouter, Depends, HTTPException, Request

from app.core.dependencies import verify_signed_request
from app.schemas.api_key import ApiKeyContext
from app.schemas.kem import (
    EncapsulationRequest,
    EncapsulationResponse,
    DecapsulationRequest,
    DecapsulationResponse
)
from app.services.pqc_operation_service import run_kem_decapsulation, run_kem_encapsulation

router = APIRouter()

@router.post(
    "/kem/encapsulate",
    response_model=EncapsulationResponse,
    summary="KEM Encapsulate",
    description="Encapsulate a shared secret using a public key."
)
def kem_encapsulate(
    request: EncapsulationRequest,
    http_request: Request,
    api_key_context: ApiKeyContext = Depends(verify_signed_request),
):
    try:
        return EncapsulationResponse(
            **run_kem_encapsulation(
                api_key_context=api_key_context,
                algorithm=request.algorithm,
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
        raise HTTPException(status_code=500, detail=f"KEM encapsulation failed: {exc}") from exc

@router.post(
    "/kem/decapsulate",
    response_model=DecapsulationResponse,
    summary="KEM Decapsulate",
    description="Decapsulate a shared secret using a private key."
)
def kem_decapsulate(
    request: DecapsulationRequest,
    http_request: Request,
    api_key_context: ApiKeyContext = Depends(verify_signed_request),
):
    try:
        return DecapsulationResponse(
            **run_kem_decapsulation(
                api_key_context=api_key_context,
                algorithm=request.algorithm,
                ciphertext=request.ciphertext,
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
        raise HTTPException(status_code=500, detail=f"KEM decapsulation failed: {exc}") from exc
