from datetime import datetime

from sqlalchemy.orm import Session

from app.models.api_nonce import ApiNonce
from app.repositories._types import as_uuid, normalize_uuid_fields


class APINonceRepository:
    def get_by_key_and_nonce(self, db: Session, api_key_id: str, nonce: str):
        return (
            db.query(ApiNonce)
            .filter(ApiNonce.api_key_id == as_uuid(api_key_id), ApiNonce.nonce == nonce)
            .first()
        )

    def create(self, db: Session, nonce_data: dict):
        api_nonce = ApiNonce(**normalize_uuid_fields(nonce_data, "id", "api_key_id"))
        db.add(api_nonce)
        db.commit()
        db.refresh(api_nonce)
        return api_nonce

    def delete_created_before(self, db: Session, cutoff: datetime) -> int:
        deleted = (
            db.query(ApiNonce)
            .filter(ApiNonce.created_at < cutoff)
            .delete(synchronize_session=False)
        )
        db.commit()
        return deleted
