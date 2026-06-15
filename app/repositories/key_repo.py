from sqlalchemy.orm import Session
from app.models.key import Key
from app.repositories._types import as_uuid, normalize_uuid_fields

class KeyRepository:

    def get_all(self, db: Session):
        return db.query(Key).all()

    def get_by_id(self, db: Session, key_id: str):
        return db.query(Key).filter(Key.id == as_uuid(key_id)).first()

    def create(self, db: Session, key_data: dict):
        key = Key(
            **normalize_uuid_fields(key_data, "id", "user_id", "algorithm_id")
        )
        db.add(key)
        db.commit()
        db.refresh(key)
        return key

    def update(self, db: Session, key_id: str, update_data: dict):
        key = self.get_by_id(db, key_id)

        if not key:
            return None

        for k, v in update_data.items():
            setattr(key, k, v)

        db.commit()
        db.refresh(key)
        return key

    def delete(self, db: Session, key_id: str):
        key = self.get_by_id(db, key_id)

        if not key:
            return None

        db.delete(key)
        db.commit()
        return key