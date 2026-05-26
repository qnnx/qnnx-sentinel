import json
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal
from app.models.audit_log import AuditLog
from app.repositories.audit_log_repo import AuditLogRepository

audit_log_repository = AuditLogRepository()


def _serialize_audit_log(log: AuditLog) -> dict:
    return {
        "id": str(log.id),
        "action": log.action,
        "actor_id": str(log.actor_id) if log.actor_id else None,
        "details": log.details,
        "created_at": log.created_at.isoformat() if log.created_at else None,
    }


def _normalize_details(details) -> str | None:
    if details is None:
        return None
    if isinstance(details, str):
        return details
    try:
        return json.dumps(details)
    except TypeError:
        return str(details)


def create_audit_log(action: str, actor_id: str | None = None, details=None) -> dict:
    if not action or not action.strip():
        raise HTTPException(status_code=400, detail="action is required")

    db = SessionLocal()
    try:
        log = audit_log_repository.create(
            db,
            {
                "id": uuid4(),
                "action": action.strip(),
                "actor_id": actor_id,
                "details": _normalize_details(details),
            },
        )
        return _serialize_audit_log(log)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create audit log") from exc
    finally:
        db.close()


def get_user_audit_logs(actor_id: str) -> list[dict]:
    if not actor_id:
        raise HTTPException(status_code=400, detail="actor_id is required")

    db = SessionLocal()
    try:
        logs = audit_log_repository.get_by_actor_id(db, actor_id)
        return [_serialize_audit_log(log) for log in logs]
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail="Failed to fetch audit logs") from exc
    finally:
        db.close()


def get_audit_logs_by_event(action: str) -> list[dict]:
    if not action or not action.strip():
        raise HTTPException(status_code=400, detail="action is required")

    db = SessionLocal()
    try:
        logs = audit_log_repository.get_by_action(db, action.strip())
        return [_serialize_audit_log(log) for log in logs]
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail="Failed to fetch audit logs") from exc
    finally:
        db.close()
