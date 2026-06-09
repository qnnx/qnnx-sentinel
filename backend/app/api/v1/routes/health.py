from fastapi import APIRouter
from app.schemas.health import HealthResponse
from app.services.health_service import get_health_status

router = APIRouter()

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Returns current status of the QNNX-Sentinel backend service."
)
def health_check():
    return get_health_status()