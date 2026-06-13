from sqlalchemy.orm import Session
import uuid
from app.models.audit_log import AuditLog
from datetime import datetime, timezone

class AuditLogRepository:
    def get_all(self, db: Session):
        return db.query(AuditLog).all()

    def get_by_id(self, db: Session, log_id: str):
        return db.query(AuditLog).filter(AuditLog.id == log_id).first()

    def get_by_user_id(self, db: Session, user_id: str):
        return db.query(AuditLog).filter(AuditLog.user_id == user_id).all()

    def get_by_action(self, db: Session, action: str):
        return db.query(AuditLog).filter(AuditLog.event_type == action).all()



    def create(self, db: Session, log_data: dict):
        from datetime import datetime, timezone
        import traceback
        
        # Ensure ID and Timestamp exist
        if "id" not in log_data:
            import uuid
            log_data["id"] = str(uuid.uuid4())
        
        if not log_data.get("created_at"):
            log_data["created_at"] = datetime.now(timezone.utc)
            
        try:
            log = AuditLog(**log_data)
            db.add(log)
            db.commit()
            db.refresh(log)
            return log
        except Exception as e:
            # THIS IS THE CRITICAL LINE
            print(f"\n!!! DATABASE CRASH: {e}")
            traceback.print_exc() 
            db.rollback()
            raise e

        

    def delete(self, db: Session, log_id: str):
        log = self.get_by_id(db, log_id)
        if not log:
            return None

        db.delete(log)
        db.commit()
        return log
