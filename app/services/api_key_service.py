from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal
from app.models.api_key import ApiKey
from app.repositories.api_key_repo import APIKeyRepository
from app.services.audit_log_service import create_audit_log
from app.utils.crypto import generate_token, sha256_hex

api_key_repository = APIKeyRepository()


def _generate_raw_api_key() -> str:
    return f"qnnx_{generate_token(32)}"


def _generate_signing_secret() -> str:
    return f"qnnxsig_{generate_token(32)}"


def _serialize_api_key(api_key: ApiKey) -> dict:
    return {
        "id": str(api_key.id),
        "user_id": str(api_key.user_id),
        "key_prefix": api_key.key_prefix,
        "name": api_key.name,
        "is_active": (api_key.status or "").lower() == "active" and api_key.revoked_at is None,
        "created_at": api_key.created_at.isoformat() if api_key.created_at else None,
        "revoked_at": api_key.revoked_at.isoformat() if api_key.revoked_at else None,
    }


def create_api_key(user_id: str, name: str) -> dict:
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    if not name or not name.strip():
        raise HTTPException(status_code=400, detail="name is required")

    raw_api_key = _generate_raw_api_key()
    signing_secret = _generate_signing_secret()
    key_hash = sha256_hex(raw_api_key)
    signing_secret_hash = sha256_hex(signing_secret)

    db = SessionLocal()
    try:
        api_key = api_key_repository.create(
            db,
            {
                "id": uuid4(),
                "user_id": user_id,
                "key_prefix": raw_api_key[:12],
                "name": name.strip(),
                "key_hash": key_hash,
                "signing_secret_hash": signing_secret_hash,
                "status": "active",
            },
        )
        response = _serialize_api_key(api_key)
        response["api_key"] = raw_api_key
        response["signing_secret"] = signing_secret
        try:
            create_audit_log(
                action="API_KEY_CREATED",
                user_id=str(api_key.user_id),
                api_key_id=str(api_key.id),
                status="success",
                details={
                    "timestamp": api_key.created_at.isoformat() if api_key.created_at else None,
                    "key_prefix": api_key.key_prefix,
                    "name": api_key.name,
                },
            )
        except HTTPException:
            pass
        return response
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create API key") from exc
    finally:
        db.close()


def get_user_api_keys(user_id: str) -> list[dict]:
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    db = SessionLocal()
    try:
        api_keys = api_key_repository.get_by_user_id(db, user_id)
        active_api_keys = [
            api_key for api_key in api_keys
            if api_key.revoked_at is None and (api_key.status or "").lower() == "active"
        ]
        return [_serialize_api_key(api_key) for api_key in active_api_keys]
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail="Failed to fetch API keys") from exc
    finally:
        db.close()


def revoke_api_key(api_key_id: str, user_id: str) -> dict:
    if not api_key_id:
        raise HTTPException(status_code=400, detail="api_key_id is required")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")

    db = SessionLocal()
    try:
        api_key = api_key_repository.get_by_id(db, api_key_id)
        if not api_key:
            raise HTTPException(status_code=404, detail="API key not found")
        if str(api_key.user_id) != str(user_id):
            raise HTTPException(status_code=403, detail="You are not allowed to revoke this API key")
        api_key = api_key_repository.revoke(db, api_key_id)
        try:
            create_audit_log(
                action="API_KEY_REVOKED",
                user_id=str(api_key.user_id),
                api_key_id=str(api_key.id),
                status="success",
                details={
                    "timestamp": api_key.revoked_at.isoformat() if api_key.revoked_at else None,
                    "key_prefix": api_key.key_prefix,
                    "name": api_key.name,
                },
            )
        except HTTPException:
            pass
        return _serialize_api_key(api_key)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to revoke API key") from exc
    finally:
        db.close()
