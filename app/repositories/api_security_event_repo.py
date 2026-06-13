import uuid
from sqlalchemy.orm import Session

from app.models.api_security_event import ApiSecurityEvent


class APISecurityEventRepository:
    def create(self, db: Session, event_data: dict):
        # 1. Ensure ID exists before hitting the database
        if "id" not in event_data or not event_data["id"]:
            event_data["id"] = str(uuid.uuid4())
            
        try:
            event = ApiSecurityEvent(**event_data)
            db.add(event)
            db.commit()
            db.refresh(event)
            return event
        except Exception as e:
            # 2. Safely rollback if anything goes wrong so the DB doesn't lock
            db.rollback()
            raise e