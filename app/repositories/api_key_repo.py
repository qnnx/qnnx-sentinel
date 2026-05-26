from sqlalchemy.orm import Session

from app.models.api_key import ApiKey


class APIKeyRepository:

    def get_all(self, db: Session):
        return db.query(ApiKey).all()

    def get_by_id(self, db: Session, api_key_id: str):
        return db.query(ApiKey).filter(ApiKey.id == api_key_id).first()

    def get_by_hash(self, db: Session, key_hash: str):
        return db.query(ApiKey).filter(ApiKey.key_hash == key_hash).first()

    def get_by_user_id(self, db: Session, user_id: str):
        return db.query(ApiKey).filter(ApiKey.user_id == user_id).all()

    def create(self, db: Session, api_key_data: dict):
        api_key = ApiKey(**api_key_data)
        db.add(api_key)
        db.commit()
        db.refresh(api_key)
        return api_key

    def update(self, db: Session, api_key_id: str, update_data: dict):
        api_key = self.get_by_id(db, api_key_id)

        if not api_key:
            return None

        for key, value in update_data.items():
            setattr(api_key, key, value)

        db.commit()
        db.refresh(api_key)
        return api_key

    def revoke(self, db: Session, api_key_id: str):
        return self.update(db, api_key_id, {"status": "revoked"})

    def delete(self, db: Session, api_key_id: str):
        api_key = self.get_by_id(db, api_key_id)

        if not api_key:
            return None

        db.delete(api_key)
        db.commit()

        return api_key
