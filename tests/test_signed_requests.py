import json
import uuid
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from app.models.api_key import ApiKey
from app.models.api_security_event import ApiSecurityEvent
from app.security.request_signature import create_request_signature
from tests.conftest import (
    TEST_API_KEY,
    TEST_API_KEY_ID,
    TEST_SIGNING_SECRET,
)

PATH = "/api/v1/keygen"


def _signed_request(body: dict, *, timestamp=None, nonce=None, signature=None):
    body_bytes = json.dumps(body, separators=(",", ":")).encode("utf-8")
    timestamp = timestamp or datetime.now(timezone.utc).isoformat()
    nonce = nonce or str(uuid.uuid4())
    signature = signature or create_request_signature(
        method="POST",
        path=PATH,
        timestamp=timestamp,
        nonce=nonce,
        body=body_bytes,
        secret=TEST_SIGNING_SECRET,
    )
    headers = {
        "Authorization": f"Bearer {TEST_API_KEY}",
        "X-QNNX-Signing-Secret": TEST_SIGNING_SECRET,
        "X-QNNX-Timestamp": timestamp,
        "X-QNNX-Nonce": nonce,
        "X-QNNX-Signature": signature,
        "Content-Type": "application/json",
    }
    return body_bytes, headers


def test_signed_request_and_replay_protection(client, db_session):
    settings.DISABLE_SIGNED_REQUEST_GUARDS = False
    try:
        body, headers = _signed_request({"algorithm": "ML-KEM-768"})
        first = client.post(PATH, content=body, headers=headers)
        assert first.status_code == 200, first.text

        replay = client.post(PATH, content=body, headers=headers)
        assert replay.status_code == 401
        assert replay.json()["error"] == "Replay attack detected"

        event = (
            db_session.query(ApiSecurityEvent)
            .filter(ApiSecurityEvent.event_type == "REPLAY_ATTACK")
            .order_by(ApiSecurityEvent.created_at.desc())
            .first()
        )
        assert event is not None
    finally:
        settings.DISABLE_SIGNED_REQUEST_GUARDS = True


def test_tampered_expired_and_invalid_signatures_are_rejected(client):
    settings.DISABLE_SIGNED_REQUEST_GUARDS = False
    try:
        original, headers = _signed_request({"algorithm": "ML-KEM-768"})
        tampered = json.dumps(
            {"algorithm": "ML-KEM-1024"},
            separators=(",", ":"),
        ).encode("utf-8")
        assert client.post(PATH, content=tampered, headers=headers).status_code == 401

        expired_timestamp = (
            datetime.now(timezone.utc) - timedelta(minutes=10)
        ).isoformat()
        expired_body, expired_headers = _signed_request(
            {"algorithm": "ML-KEM-768"},
            timestamp=expired_timestamp,
        )
        assert client.post(
            PATH,
            content=expired_body,
            headers=expired_headers,
        ).status_code == 401

        invalid_body, invalid_headers = _signed_request(
            {"algorithm": "ML-KEM-768"},
            signature="invalid",
        )
        assert client.post(
            PATH,
            content=invalid_body,
            headers=invalid_headers,
        ).status_code == 401
    finally:
        settings.DISABLE_SIGNED_REQUEST_GUARDS = True


def test_revoked_key_is_rejected(client, db_session):
    api_key = db_session.get(ApiKey, TEST_API_KEY_ID)
    api_key.status = "revoked"
    api_key.revoked_at = datetime.now(timezone.utc)
    db_session.commit()

    settings.DISABLE_SIGNED_REQUEST_GUARDS = False
    try:
        body, headers = _signed_request({"algorithm": "ML-KEM-768"})
        response = client.post(PATH, content=body, headers=headers)
        assert response.status_code == 401
        assert response.json()["error"] == "Invalid API key"
    finally:
        settings.DISABLE_SIGNED_REQUEST_GUARDS = True
        api_key.status = "active"
        api_key.revoked_at = None
        db_session.commit()
