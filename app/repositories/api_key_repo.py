from sqlalchemy.orm import Session
from app.models.api_key import ApiKey
import secrets


class APIKeyRepository:

    def get_all(self, db: Session):
        return db.query(ApiKey).all()

    def get_by_id(self, db: Session, api_key_id: str):
        return db.query(ApiKey).filter(ApiKey.id == api_key_id).first()

    def get_by_key(self, db: Session, api_key: str):
        return db.query(ApiKey).filter(ApiKey.api_key == api_key).first()

    def create(self, db: Session, name: str):
        generated_key = f"qnnx_{secrets.token_urlsafe(32)}"

        api_key = ApiKey(
            name=name,
            api_key=generated_key,
            is_active=True
        )

        db.add(api_key)
        db.commit()
        db.refresh(api_key)

        return api_key

    def revoke(self, db: Session, api_key_id: str):
        api_key = self.get_by_id(db, api_key_id)

        if not api_key:
            return None

        api_key.is_active = False

        db.commit()
        db.refresh(api_key)

        return api_key

    def delete(self, db: Session, api_key_id: str):
        api_key = self.get_by_id(db, api_key_id)

        if not api_key:
            return None

        db.delete(api_key)
        db.commit()

        return api_key
