from fastapi import APIRouter, HTTPException, Query

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

@router.get(
    "/api-keys",
    response_model=list[ApiKeyResponse],
    summary="Get API Keys",
    description="Returns all API keys for the provided user ID."
)
def get_api_keys(user_id: str = Query(...)):
    try:
        api_keys = get_user_api_keys(user_id)
        return [ApiKeyResponse(**api_key) for api_key in api_keys]
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch API keys: {exc}") from exc

@router.post(
    "/api-keys",
    response_model=CreateApiKeyResponse,
    summary="Create API Key",
    description="Creates a new API key for the provided user ID and returns it once."
)
def create_api_key(request: CreateApiKeyRequest):
    try:
        api_key = create_api_key_service(request.user_id, request.name)
        return CreateApiKeyResponse(**api_key)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to create API key: {exc}") from exc


@router.post(
    "/api-keys/revoke",
    response_model=ApiKeyResponse,
    summary="Revoke API Key",
    description="Changes the API key status to revoked when the provided user owns the key.",
)
def revoke_api_key(request: RevokeApiKeyRequest):
    try:
        api_key = revoke_api_key_service(request.api_key_id, request.user_id)
        return ApiKeyResponse(**api_key)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to revoke API key: {exc}") from exc
