from sqlalchemy.orm import Session

from app.models.api_nonce import ApiNonce


class APINonceRepository:
    def get_by_key_and_nonce(self, db: Session, api_key_id: str, nonce: str):
        return (
            db.query(ApiNonce)
            .filter(ApiNonce.api_key_id == api_key_id, ApiNonce.nonce == nonce)
            .first()
        )

    def create(self, db: Session, nonce_data: dict):
        api_nonce = ApiNonce(**nonce_data)
        db.add(api_nonce)
        db.commit()
        db.refresh(api_nonce)
        return api_nonce