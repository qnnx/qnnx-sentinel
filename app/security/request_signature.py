import json
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException

from app.utils.crypto import constant_time_compare, hmac_sha256_hex


def extract_bearer_token(authorization: str | None) -> str | None:
    if not authorization:
        return None

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token.strip():
        return None
    return token.strip()


def extract_algorithm(payload: Any) -> str | None:
    if isinstance(payload, dict):
        algorithm = payload.get("algorithm")
        if isinstance(algorithm, str) and algorithm.strip():
            return algorithm.strip()
    return None


def parse_json_body(body: bytes) -> dict[str, Any] | None:
    if not body:
        return {}

    try:
        data = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=400, detail="Request body must be valid JSON") from exc

    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="Request body must be a JSON object")
    return data


def build_signature_payload(
    method: str,
    path: str,
    timestamp: str,
    nonce: str,
    body: bytes,
) -> bytes:
    return (
        method.upper().encode("utf-8")
        + path.encode("utf-8")
        + timestamp.encode("utf-8")
        + nonce.encode("utf-8")
        + body
    )


def create_request_signature(
    method: str,
    path: str,
    timestamp: str,
    nonce: str,
    body: bytes,
    secret: str,
) -> str:
    payload = build_signature_payload(method, path, timestamp, nonce, body)
    return hmac_sha256_hex(secret, payload)


def verify_request_signature(
    provided_signature: str,
    method: str,
    path: str,
    timestamp: str,
    nonce: str,
    body: bytes,
    secret: str,
) -> bool:
    expected_signature = create_request_signature(
        method=method,
        path=path,
        timestamp=timestamp,
        nonce=nonce,
        body=body,
        secret=secret,
    )
    return constant_time_compare(provided_signature, expected_signature)


def is_timestamp_fresh(timestamp: str, ttl_seconds: int) -> bool:
    parsed_timestamp = parse_request_timestamp(timestamp)
    now = datetime.now(timezone.utc)
    oldest_allowed = now - timedelta(seconds=ttl_seconds)
    newest_allowed = now + timedelta(seconds=ttl_seconds)
    return oldest_allowed <= parsed_timestamp <= newest_allowed


def parse_request_timestamp(timestamp: str) -> datetime:
    normalized = timestamp.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"

    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid X-QNNX-Timestamp format") from exc

    if parsed.tzinfo is None:
        raise HTTPException(status_code=400, detail="X-QNNX-Timestamp must include timezone information")

    return parsed.astimezone(timezone.utc)
