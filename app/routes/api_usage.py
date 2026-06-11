from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()

class UsageStat(BaseModel):
    endpoint: str
    total_calls: int
    last_called: str

MOCK_USAGE = [
    UsageStat(
        endpoint="/api/v1/kem/encapsulate",
        total_calls=150,
        last_called="2026-06-10T12:00:00"
    ),
    UsageStat(
        endpoint="/api/v1/kem/decapsulate",
        total_calls=148,
        last_called="2026-06-10T12:01:00"
    ),
    UsageStat(
        endpoint="/api/v1/sign",
        total_calls=200,
        last_called="2026-06-10T11:00:00"
    ),
    UsageStat(
        endpoint="/api/v1/verify",
        total_calls=195,
        last_called="2026-06-10T11:05:00"
    ),
    UsageStat(
        endpoint="/api/v1/algorithms",
        total_calls=300,
        last_called="2026-06-10T10:00:00"
    ),
]

@router.get(
    "/api-usage",
    response_model=List[UsageStat],
    summary="Get API Usage",
    description="Returns API usage statistics for all endpoints."
)
def get_usage():
    return MOCK_USAGE
