from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog


class AuditLogRepository:

    def get_all(self, db: Session):
        return db.query(AuditLog).all()

    def get_by_id(self, db: Session, log_id: str):
        return db.query(AuditLog).filter(AuditLog.id == log_id).first()
   def update(self, db: Session, log_id: str, update_data: dict):
    log = self.get_by_id(db, log_id)

<<<<<<< HEAD
    if not log:
        return None

    for key, value in update_data.items():
        setattr(log, key, value)

    db.commit()
    db.refresh(log)

    return log
    
=======
    def get_by_actor_id(self, db: Session, actor_id: str):
        return db.query(AuditLog).filter(AuditLog.actor_id == actor_id).all()

    def get_by_action(self, db: Session, action: str):
        return db.query(AuditLog).filter(AuditLog.action == action).all()

>>>>>>> 4a987a9d0f44393fbbb5cda33d01cbe5d5eb36fa
    def create(self, db: Session, log_data: dict):
        log = AuditLog(**log_data)
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    def delete(self, db: Session, log_id: str):
        log = self.get_by_id(db, log_id)

        if not log:
            return None

        db.delete(log)
        db.commit()
        return log
