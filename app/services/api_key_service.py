import hashlib
import secrets
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal
from app.models.api_key import ApiKey
from app.repositories.api_key_repo import APIKeyRepository

api_key_repository = APIKeyRepository()


def _generate_raw_api_key() -> str:
    return f"qnnx_{secrets.token_urlsafe(32)}"


def _hash_api_key(raw_api_key: str) -> str:
    return hashlib.sha256(raw_api_key.encode("utf-8")).hexdigest()


def _serialize_api_key(api_key: ApiKey) -> dict:
    return {
        "id": str(api_key.id),
        "user_id": str(api_key.user_id),
        "name": api_key.name,
        "status": api_key.status,
        "last_used_at": api_key.last_used_at.isoformat() if api_key.last_used_at else None,
        "created_at": api_key.created_at.isoformat() if api_key.created_at else None,
    }


def create_api_key(user_id: str, name: str) -> dict:
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id is required")
    if not name or not name.strip():
        raise HTTPException(status_code=400, detail="name is required")

    raw_api_key = _generate_raw_api_key()
    key_hash = _hash_api_key(raw_api_key)

    db = SessionLocal()
    try:
        api_key = api_key_repository.create(
            db,
            {
                "id": uuid4(),
                "user_id": user_id,
                "name": name.strip(),
                "key_hash": key_hash,
                "status": "active",
            },
        )
        response = _serialize_api_key(api_key)
        response["api_key"] = raw_api_key
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
            if (api_key.status or "").lower() != "revoked"
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
        if str(api_key.user_id) != user_id:
            raise HTTPException(status_code=403, detail="You are not allowed to revoke this API key")
        api_key = api_key_repository.revoke(db, api_key_id)
        return _serialize_api_key(api_key)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to revoke API key") from exc
    finally:
        db.close()
