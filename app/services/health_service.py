from app.core.config import settings
from app.schemas.health import HealthResponse

def get_health_status() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        service=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT
    )
