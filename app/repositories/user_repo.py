from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories._types import as_uuid, normalize_uuid_fields


class UserRepository:

    def get_all(self, db: Session):
        return db.query(User).all()

    def get_by_id(self, db: Session, user_id: str):
        return db.query(User).filter(User.id == as_uuid(user_id)).first()

    def create(self, db: Session, user_data: dict):
        user = User(**normalize_uuid_fields(user_data, "id"))
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def update(self, db: Session, user_id: str, update_data: dict):
        user = self.get_by_id(db, user_id)

        if not user:
            return None

        for key, value in update_data.items():
            setattr(user, key, value)

        db.commit()
        db.refresh(user)
        return user

    def delete(self, db: Session, user_id: str):
        user = self.get_by_id(db, user_id)

        if not user:
            return None

        db.delete(user)
        db.commit()
        return user