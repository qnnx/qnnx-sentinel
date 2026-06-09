from sqlalchemy.orm import Session
from app.models.key import Key

class KeyRepository:

    def get_all(self, db: Session):
        return db.query(Key).all()

    def get_by_id(self, db: Session, key_id: str):
        return db.query(Key).filter(Key.id == key_id).first()

    def create(self, db: Session, key_data: dict):
        key = Key(**key_data)
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