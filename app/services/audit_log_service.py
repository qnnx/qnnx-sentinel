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
        "event_type": log.event_type,
        "resource_type": log.resource_type,
        "resource_id": log.resource_id,
        "status": log.status,
        "user_id": str(log.user_id) if log.user_id else None,
        "api_key_id": str(log.api_key_id) if log.api_key_id else None,
        "ip_address": log.ip_address,
        "details": log.details,
        "created_at": log.created_at.isoformat() if log.created_at else None,
    }


def _normalize_details(details):
    if details is None:
        return None
    if isinstance(details, dict):
        return details
    if isinstance(details, str):
        return {"message": details}
    return {"value": str(details)}


def create_audit_log(
    action: str,
    user_id: str | None = None,
    api_key_id: str | None = None,
    status: str | None = None,
    ip_address: str | None = None,
    resource_type: str | None = None,
    resource_id: str | None = None,
    details=None,
) -> dict:
    if not action or not action.strip():
        raise HTTPException(status_code=400, detail="action is required")

    db = SessionLocal()
    try:
        log = audit_log_repository.create(
            db,
            {
                "id": uuid4(),
                "event_type": action.strip(),
                "status": status or "success",
                "user_id": user_id,
                "api_key_id": api_key_id,
                "ip_address": ip_address,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "details": _normalize_details(details),
            },
        )
        db.commit() # Ensure the commit is explicit!
        return _serialize_audit_log(log)
    except SQLAlchemyError as exc:
        db.rollback()
        # CRITICAL: Print the real error to the terminal
        print(f"!!! AUDIT LOG DATABASE ERROR: {repr(exc)}") 
        raise HTTPException(status_code=500, detail=f"Audit log failed: {str(exc)}")
    finally:
        db.close()

def get_user_audit_logs(user_id: str) -> list[dict]:
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    db = SessionLocal()
    try:
        logs = audit_log_repository.get_by_user_id(db, user_id)
        return [_serialize_audit_log(log) for log in logs]
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail="Failed to fetch audit logs") from exc
    finally:
        db.close()


def get_audit_log_by_id(user_id: str, log_id: str) -> dict:
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    if not log_id:
        raise HTTPException(status_code=400, detail="log_id is required")

    db = SessionLocal()
    try:
        log = audit_log_repository.get_by_id(db, log_id)
        if not log or str(log.user_id) != str(user_id):
            raise HTTPException(status_code=404, detail="Audit log not found")
        return _serialize_audit_log(log)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail="Failed to fetch audit log") from exc
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