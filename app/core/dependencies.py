import hashlib
import time
from datetime import datetime, timezone

from fastapi import Header, HTTPException, Request, Response
from sqlalchemy.exc import SQLAlchemyError

from app.core.database import SessionLocal
from app.repositories.api_key_repo import APIKeyRepository
from app.services.api_usage_service import record_api_usage
from app.services.audit_log_service import create_audit_log

api_key_repository = APIKeyRepository()


def _hash_api_key(raw_api_key: str) -> str:
    return hashlib.sha256(raw_api_key.encode("utf-8")).hexdigest()


def _serialize_api_key(api_key) -> dict:
    return {
        "id": str(api_key.id),
        "user_id": str(api_key.user_id),
        "name": api_key.name,
        "status": api_key.status,
        "last_used_at": api_key.last_used_at.isoformat() if api_key.last_used_at else None,
        "created_at": api_key.created_at.isoformat() if api_key.created_at else None,
    }

async def get_db():
    # Placeholder - baad mein real database connection aayega
    db = None
    try:
        yield db
    finally:
        pass

async def get_current_user(authorization: str = Header(None)):
    # Placeholder - baad mein real authentication aayega
    if authorization is None:
        return {"id": "mock-user", "name": "Mock User", "role": "admin"}
    return {"id": "mock-user", "name": "Mock User", "role": "admin"}

def _extract_algorithm(payload) -> str | None:
    if isinstance(payload, dict):
        algorithm = payload.get("algorithm")
        if isinstance(algorithm, str) and algorithm.strip():
            return algorithm.strip()
    return None


def _log_invalid_api_key(request: Request, provided_key: str | None):
    try:
        create_audit_log(
            action="INVALID_API_KEY",
            details={
                "path": request.url.path,
                "method": request.method,
                "provided": bool(provided_key and provided_key.strip()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )
    except HTTPException:
        pass


def _log_authenticated_request(api_key_info: dict, request: Request):
    try:
        create_audit_log(
            action="API_REQUEST_AUTHENTICATED",
            actor_id=api_key_info.get("user_id"),
            details={
                "path": request.url.path,
                "method": request.method,
                "api_key_id": api_key_info.get("id"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )
    except HTTPException:
        pass


def _record_authenticated_usage(
    api_key_info: dict,
    request: Request,
    response_status: int,
    response_time_ms: int,
):
    try:
        record_api_usage(
            actor_id=api_key_info.get("user_id"),
            endpoint=request.url.path,
            http_method=request.method,
            algorithm=getattr(request.state, "algorithm", None),
            response_status=response_status,
            response_time_ms=response_time_ms,
        )
    except HTTPException:
        pass


async def validate_api_key(
    request: Request,
    response: Response,
    x_api_key: str = Header(None, alias="X-API-Key"),
):
    if not x_api_key or not x_api_key.strip():
        _log_invalid_api_key(request, x_api_key)
        raise HTTPException(status_code=401, detail="Invalid or inactive API key")

    start_time = time.perf_counter()

    try:
        payload = await request.json()
    except Exception:
        payload = None

    request.state.algorithm = _extract_algorithm(payload)

    db = SessionLocal()
    try:
        key_hash = _hash_api_key(x_api_key.strip())
        api_key = api_key_repository.get_by_hash(db, key_hash)

        if not api_key or api_key.status.lower() != "active":
            _log_invalid_api_key(request, x_api_key)
            raise HTTPException(status_code=401, detail="Invalid or inactive API key")

        api_key = api_key_repository.update(
            db,
            str(api_key.id),
            {"last_used_at": datetime.now(timezone.utc)},
        )
        api_key_info = _serialize_api_key(api_key)
        _log_authenticated_request(api_key_info, request)
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to validate API key") from exc
    finally:
        db.close()

    try:
        yield api_key_info
    finally:
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)
        response_status = getattr(response, "status_code", 200)
        _record_authenticated_usage(api_key_info, request, response_status, elapsed_ms)
