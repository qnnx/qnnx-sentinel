from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.api_key import ApiKey
from app.repositories._types import as_uuid


class APIKeyRepository:
    def get_by_hash(self, db: Session, key_hash: str):
        return db.query(ApiKey).filter(ApiKey.key_hash == key_hash).first()

    def mark_used(self, db: Session, api_key_id: str):
        api_key = db.query(ApiKey).filter(ApiKey.id == as_uuid(api_key_id)).first()
        if not api_key:
            return None

        api_key.last_used_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(api_key)
        return api_key
