from sqlalchemy.orm import Session
from app.models.api_usage import ApiUsage
from datetime import datetime, timezone
import uuid

class ApiUsageRepository:

    def get_all(self, db: Session):
        return db.query(ApiUsage).all()

    def get_by_id(self, db: Session, usage_id: str):
        return db.query(ApiUsage).filter(ApiUsage.id == usage_id).first()

    def get_by_actor_id(self, db: Session, actor_id: str):
        return db.query(ApiUsage).filter(ApiUsage.actor_id == actor_id).all()

    def get_recent_by_actor_id(self, db: Session, actor_id: str, limit: int = 10):
        return (
            db.query(ApiUsage)
            .filter(ApiUsage.actor_id == actor_id)
            .order_by(ApiUsage.created_at.desc())
            .limit(limit)
            .all()
        )

    def create(self, db: Session, usage_data: dict):
    # Ensure ID exists
        if "id" not in usage_data or not usage_data["id"]:
            usage_data["id"] = str(uuid.uuid4())
        
    # THE FIX: Ensure created_at exists
        if not usage_data.get("created_at"):
            usage_data["created_at"] = datetime.now(timezone.utc)
        
        try:
        # Note: If your model is named differently (like UsageLog), change ApiUsage below to match your import
            usage = ApiUsage(**usage_data) 
            db.add(usage)
            db.commit()
            db.refresh(usage)
            return usage
        except Exception as e:
            db.rollback()
        raise e

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