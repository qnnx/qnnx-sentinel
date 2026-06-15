from sqlalchemy.orm import Session

from app.models.api_security_event import ApiSecurityEvent
from app.repositories._types import normalize_uuid_fields


class APISecurityEventRepository:
    def create(self, db: Session, event_data: dict):
        event = ApiSecurityEvent(
            **normalize_uuid_fields(event_data, "id", "user_id", "api_key_id")
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event