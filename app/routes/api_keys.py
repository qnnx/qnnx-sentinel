from fastapi import APIRouter
from typing import List
from pydantic import BaseModel

router = APIRouter()

class APIKey(BaseModel):
    id: str
    name: str
    key: str
    created_at: str

class CreateAPIKeyRequest(BaseModel):
    name: str

MOCK_API_KEYS = [
    APIKey(
        id="key-001",
        name="Test Key 1",
        key="sk-mock-key-001",
        created_at="2026-01-01T00:00:00"
    ),
    APIKey(
        id="key-002",
        name="Test Key 2",
        key="sk-mock-key-002",
        created_at="2026-01-02T00:00:00"
    ),
]

@router.get(
    "/api-keys",
    response_model=List[APIKey],
    summary="Get API Keys",
    description="Returns all API keys."
)
def get_api_keys():
    return MOCK_API_KEYS

@router.post(
    "/api-keys",
    response_model=APIKey,
    summary="Create API Key",
    description="Create a new API key."
)
def create_api_key(request: CreateAPIKeyRequest):
    return APIKey(
        id="key-003",
        name=request.name,
        key="sk-mock-key-003",
        created_at="2026-06-10T00:00:00"
    )