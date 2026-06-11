from typing import List

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel

from app.services.api_key_service import (
    create_api_key as create_api_key_service,
    get_user_api_keys,
    revoke_api_key as revoke_api_key_service,
)

router = APIRouter()

class APIKeyResponse(BaseModel):
    id: str
    user_id: str
    name: str
    status: str
    last_used_at: str | None = None
    created_at: str


class CreateAPIKeyRequest(BaseModel):
    user_id: str
    name: str


class GetAPIKeysRequest(BaseModel):
    user_id: str


class CreateAPIKeyResponse(APIKeyResponse):
    api_key: str


class RevokeAPIKeyRequest(BaseModel):
    api_key_id: str
    user_id: str

@router.get(
    "/api-keys",
    response_model=List[APIKeyResponse],
    summary="Get API Keys",
    description="Returns all API keys for the provided user ID."
)
def get_api_keys(request: GetAPIKeysRequest = Body(...)):
    try:
        api_keys = get_user_api_keys(request.user_id)
        return [APIKeyResponse(**api_key) for api_key in api_keys]
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch API keys: {exc}") from exc

@router.post(
    "/api-keys",
    response_model=CreateAPIKeyResponse,
    summary="Create API Key",
    description="Creates a new API key for the provided user ID and returns it once."
)
def create_api_key(request: CreateAPIKeyRequest):
    try:
        api_key = create_api_key_service(request.user_id, request.name)
        return CreateAPIKeyResponse(**api_key)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to create API key: {exc}") from exc


@router.post(
    "/api-keys/revoke",
    response_model=APIKeyResponse,
    summary="Revoke API Key",
    description="Changes the API key status to revoked when the provided user owns the key.",
)
def revoke_api_key(request: RevokeAPIKeyRequest):
    try:
        api_key = revoke_api_key_service(request.api_key_id, request.user_id)
        return APIKeyResponse(**api_key)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to revoke API key: {exc}") from exc
