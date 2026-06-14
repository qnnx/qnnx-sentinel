from typing import Any
from uuid import UUID

from fastapi import Header, HTTPException, Request
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.config import settings
from app.core.database import SessionLocal
from app.repositories.algorithm_repo import AlgorithmRepository
from app.repositories.api_key_repo import APIKeyRepository
from app.repositories.api_nonce_repo import APINonceRepository
from app.repositories.api_security_event_repo import APISecurityEventRepository
from app.repositories.user_repo import UserRepository
from app.schemas.api_key import ApiKeyContext
from app.security.request_signature import (
    extract_algorithm,
    extract_bearer_token,
    is_timestamp_fresh,
    parse_json_body,
    verify_request_signature,
)
from app.services.audit_log_service import create_audit_log
from app.utils.crypto import sha256_hex

REQUEST_TTL_SECONDS = 300
ACTIVE_ALGORITHM_STATUSES = {"active", "enabled","recommended"}

api_key_repository = APIKeyRepository()
api_nonce_repository = APINonceRepository()
api_security_event_repository = APISecurityEventRepository()
algorithm_repository = AlgorithmRepository()
user_repository = UserRepository()

async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_current_user(authorization: str = Header(None)):
    if authorization is None or not authorization.strip():
        raise HTTPException(status_code=401, detail="Authorization header is required")

    token = extract_bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")

    try:
        user_id = str(UUID(token))
    except ValueError as exc:
        raise HTTPException(
            status_code=401,
            detail="Authorization bearer token must be a valid public.users UUID for local testing",
        ) from exc

    db = SessionLocal()
    try:
        existing_user = user_repository.get_by_id(db, user_id)
        if not existing_user:
            raise HTTPException(
                status_code=401,
                detail="Authenticated user not found in public.users",
            )
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to resolve authenticated user") from exc
    finally:
        db.close()

    return {
        "id": str(existing_user.id),
        "name": existing_user.full_name or "Authenticated User",
        "role": existing_user.role,
    }

def _build_request_metadata(request: Request) -> dict[str, Any]:
    return {
        "endpoint": request.url.path,
        "method": request.method.upper(),
        "ip_address": request.client.host if request.client else None,
        "user_agent": request.headers.get("user-agent"),
    }


def _serialize_api_key(api_key) -> ApiKeyContext:
    return ApiKeyContext(
        id=api_key.id,
        user_id=api_key.user_id,
        key_prefix=api_key.key_prefix,
        name=api_key.name,
        is_active=(api_key.status or "").lower() == "active" and api_key.revoked_at is None,
    )


def _create_security_event(
    db,
    request: Request,
    event_type: str,
    details: dict[str, Any] | None = None,
    user_id=None,
    api_key_id=None,
):
    metadata = _build_request_metadata(request)
    try:
        api_security_event_repository.create(
            db,
            {
                "user_id": user_id,
                "api_key_id": api_key_id,
                "event_type": event_type,
                "endpoint": metadata["endpoint"],
                "method": metadata["method"],
                "ip_address": metadata["ip_address"],
                "user_agent": metadata["user_agent"],
                "details": details or {},
            },
        )
    except SQLAlchemyError:
        db.rollback()

    try:
        create_audit_log(
            action=event_type,
            user_id=str(user_id) if user_id else None,
            api_key_id=str(api_key_id) if api_key_id else None,
            status="failed",
            details={
                "endpoint": metadata["endpoint"],
                "method": metadata["method"],
                "ip_address": metadata["ip_address"],
                "user_agent": metadata["user_agent"],
                **(details or {}),
            },
        )
    except HTTPException:
        pass


def _validate_algorithm(db, request: Request, payload: dict[str, Any], api_key_context: ApiKeyContext):
    algorithm = extract_algorithm(payload)
    
    if not algorithm:
        raise HTTPException(status_code=400, detail="algorithm is required")

    record = algorithm_repository.get_by_identifier(db, algorithm)
    if not record or (record.status or "").lower() not in ACTIVE_ALGORITHM_STATUSES:
        _create_security_event(
            db,
            request,
            "UNSUPPORTED_ALGORITHM",
            details={"algorithm": algorithm},
            user_id=api_key_context.user_id,
            api_key_id=api_key_context.id,
        )
        raise HTTPException(status_code=400, detail="Unsupported or disabled algorithm")

    request.state.algorithm = record.name


async def verify_signed_request(request: Request):
    body = await request.body()
    payload = parse_json_body(body)
    request.state.raw_body = body
    request.state.algorithm = extract_algorithm(payload)

    authorization = request.headers.get("Authorization")
    signing_secret = request.headers.get("X-QNNX-Signing-Secret")
    timestamp = request.headers.get("X-QNNX-Timestamp")
    nonce = request.headers.get("X-QNNX-Nonce")
    signature = request.headers.get("X-QNNX-Signature")

    missing_headers = []
    if not authorization:
        missing_headers.append("Authorization")
    if not settings.DISABLE_SIGNED_REQUEST_GUARDS and not signing_secret:
        missing_headers.append("X-QNNX-Signing-Secret")
    if not settings.DISABLE_SIGNED_REQUEST_GUARDS and not timestamp:
        missing_headers.append("X-QNNX-Timestamp")
    if not settings.DISABLE_SIGNED_REQUEST_GUARDS and not nonce:
        missing_headers.append("X-QNNX-Nonce")
    if not settings.DISABLE_SIGNED_REQUEST_GUARDS and not signature:
        missing_headers.append("X-QNNX-Signature")

    db = SessionLocal()
    api_key_context: ApiKeyContext | None = None

    try:
        if missing_headers:
            _create_security_event(
                db,
                request,
                "MISSING_HEADERS",
                details={"missing_headers": missing_headers},
            )
            raise HTTPException(status_code=401, detail="Missing required authentication headers")

        raw_api_key = extract_bearer_token(authorization)
        if not raw_api_key:
            _create_security_event(
                db,
                request,
                "INVALID_API_KEY",
                details={"reason": "Invalid Authorization header format"},
            )
            raise HTTPException(status_code=401, detail="Invalid API key")

        api_key = api_key_repository.get_by_hash(db, sha256_hex(raw_api_key))
        if not api_key or (api_key.status or "").lower() != "active" or api_key.revoked_at is not None:
            _create_security_event(
                db,
                request,
                "INVALID_API_KEY",
                details={"key_prefix": raw_api_key[:12]},
            )
            raise HTTPException(status_code=401, detail="Invalid API key")

        if (
            not settings.DISABLE_SIGNED_REQUEST_GUARDS
            and api_key.signing_secret_hash != sha256_hex(signing_secret)
        ):
            _create_security_event(
                db,
                request,
                "INVALID_SIGNING_SECRET",
                details={"key_prefix": raw_api_key[:12]},
            )
            raise HTTPException(status_code=401, detail="Invalid signing secret")

        api_key_context = _serialize_api_key(api_key)

        if not settings.DISABLE_SIGNED_REQUEST_GUARDS:
            try:
                timestamp_is_fresh = is_timestamp_fresh(timestamp, REQUEST_TTL_SECONDS)
            except HTTPException as exc:
                _create_security_event(
                    db,
                    request,
                    "EXPIRED_REQUEST",
                    details={"timestamp": timestamp, "reason": exc.detail},
                    user_id=api_key_context.user_id,
                    api_key_id=api_key_context.id,
                )
                raise

            if not timestamp_is_fresh:
                _create_security_event(
                    db,
                    request,
                    "EXPIRED_REQUEST",
                    details={"timestamp": timestamp},
                    user_id=api_key_context.user_id,
                    api_key_id=api_key_context.id,
                )
                raise HTTPException(status_code=401, detail="Expired request")

            if not verify_request_signature(
                provided_signature=signature,
                method=request.method,
                path=request.url.path,
                timestamp=timestamp,
                nonce=nonce,
                body=body,
                secret=signing_secret,
            ):
                _create_security_event(
                    db,
                    request,
                    "INVALID_SIGNATURE",
                    details={"nonce": nonce, "timestamp": timestamp},
                    user_id=api_key_context.user_id,
                    api_key_id=api_key_context.id,
                )
                raise HTTPException(status_code=401, detail="Invalid signature")

        _validate_algorithm(db, request, payload or {}, api_key_context)

        if not settings.DISABLE_SIGNED_REQUEST_GUARDS:
            if api_nonce_repository.get_by_key_and_nonce(db, str(api_key_context.id), nonce):
                _create_security_event(
                    db,
                    request,
                    "REPLAY_ATTACK",
                    details={"nonce": nonce},
                    user_id=api_key_context.user_id,
                    api_key_id=api_key_context.id,
                )
                raise HTTPException(status_code=401, detail="Replay attack detected")

            try:
                api_nonce_repository.create(
                    db,
                    {
                        "api_key_id": api_key_context.id,
                        "nonce": nonce,
                    },
                )
            except IntegrityError as exc:
                db.rollback()
                _create_security_event(
                    db,
                    request,
                    "REPLAY_ATTACK",
                    details={"nonce": nonce, "reason": "Unique constraint violation"},
                    user_id=api_key_context.user_id,
                    api_key_id=api_key_context.id,
                )
                raise HTTPException(status_code=401, detail="Replay attack detected") from exc
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to validate signed request: {exc}") from exc
    finally:
        db.close()

    yield api_key_context


validate_api_key = verify_signed_request