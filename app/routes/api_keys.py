import logging

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_current_user
from app.schemas.api_key import (
    ApiKeyResponse,
    CreateApiKeyRequest,
    CreateApiKeyResponse,
    RevokeApiKeyRequest,
)
from app.services.api_key_service import (
    create_api_key as create_api_key_service,
    get_user_api_keys,
    revoke_api_key as revoke_api_key_service,
)

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get(
    "/api-keys",
    response_model=list[ApiKeyResponse],
    summary="Get API Keys",
    description="Returns all API keys for the authenticated user."
)
def get_api_keys(current_user=Depends(get_current_user)):
    try:
        api_keys = get_user_api_keys(current_user["id"])
        return [ApiKeyResponse(**api_key) for api_key in api_keys]
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to fetch API keys")
        raise HTTPException(status_code=500, detail="Failed to fetch API keys") from exc

@router.post(
    "/api-keys",
    response_model=CreateApiKeyResponse,
    summary="Create API Key",
    description="Creates a new API key for the authenticated user and returns it once."
)
def create_api_key(request: CreateApiKeyRequest, current_user=Depends(get_current_user)):
    try:
        api_key = create_api_key_service(current_user["id"], request.name)
        return CreateApiKeyResponse(**api_key)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to create API key")
        raise HTTPException(status_code=500, detail="Failed to create API key") from exc


@router.post(
    "/api-keys/revoke",
    response_model=ApiKeyResponse,
    summary="Revoke API Key",
    description="Changes the API key status to revoked when the provided user owns the key.",
)
def revoke_api_key(request: RevokeApiKeyRequest, current_user=Depends(get_current_user)):
    try:
        api_key = revoke_api_key_service(str(request.api_key_id), current_user["id"])
        return ApiKeyResponse(**api_key)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to revoke API key")
        raise HTTPException(status_code=500, detail="Failed to revoke API key") from exc
