from sqlalchemy.orm import Session
from app.models.api_usage import ApiUsage

class ApiUsageRepository:

    def get_all(self, db: Session):
        return db.query(ApiUsage).all()

    def get_by_id(self, db: Session, usage_id: str):
        return db.query(ApiUsage).filter(ApiUsage.id == usage_id).first()

    def create(self, db: Session, usage_data: dict):
        usage = ApiUsage(**usage_data)
        db.add(usage)
        db.commit()
        db.refresh(usage)
        return usage

    def update(self, db: Session, usage_id: str, update_data: dict):
        usage = self.get_by_id(db, usage_id)

        if not usage:
            return None

        for key, value in update_data.items():
            setattr(usage, key, value)

        db.commit()
        db.refresh(usage)
        return usage

    def delete(self, db: Session, usage_id: str):
        usage = self.get_by_id(db, usage_id)

        if not usage:
            return None

        db.delete(usage)
        db.commit()
        return usage