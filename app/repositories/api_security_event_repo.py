from sqlalchemy.orm import Session

from app.models.api_security_event import ApiSecurityEvent


class APISecurityEventRepository:
    def create(self, db: Session, event_data: dict):
        event = ApiSecurityEvent(**event_data)
        db.add(event)
        db.commit()
        db.refresh(event)
        return event
