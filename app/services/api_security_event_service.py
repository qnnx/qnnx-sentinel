from typing import Any

from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal
from app.repositories.api_security_event_repo import APISecurityEventRepository
from app.schemas.api_security_event import ApiSecurityEventResponse

api_security_event_repository = APISecurityEventRepository()


def create_api_security_event(
    event_type: str,
    endpoint: str | None = None,
    method: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    details: dict[str, Any] | None = None,
    user_id: str | None = None,
    api_key_id: str | None = None,
) -> ApiSecurityEventResponse | None:
    db = SessionLocal()
    try:
        event = api_security_event_repository.create(
            db,
            {
                "user_id": user_id,
                "api_key_id": api_key_id,
                "event_type": event_type,
                "endpoint": endpoint,
                "method": method,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "details": details,
            },
        )
        return ApiSecurityEventResponse.model_validate(event, from_attributes=True)
    except SQLAlchemyError:
        db.rollback()
        return None
    finally:
        db.close()
