from datetime import datetime, timedelta, timezone

from app.core.dependencies import _serialize_api_key
from app.repositories.api_key_repo import APIKeyRepository
from app.repositories.api_nonce_repo import APINonceRepository
from app.utils.crypto import sha256_hex
from tests.conftest import TEST_API_KEY, TEST_API_KEY_ID


def test_api_key_hash_lookup_and_serialization(db_session):
    record = APIKeyRepository().get_by_hash(db_session, sha256_hex(TEST_API_KEY))
    assert record is not None
    assert record.status == "active"
    context = _serialize_api_key(record)
    assert context.id == TEST_API_KEY_ID
    assert context.is_active is True


def test_nonce_cleanup_removes_expired_records(db_session):
    repository = APINonceRepository()
    old_nonce = repository.create(
        db_session,
        {
            "api_key_id": TEST_API_KEY_ID,
            "nonce": "expired-nonce",
            "created_at": datetime.now(timezone.utc) - timedelta(minutes=10),
        },
    )
    assert old_nonce.id is not None
    deleted = repository.delete_created_before(
        db_session,
        datetime.now(timezone.utc) - timedelta(minutes=5),
    )
    assert deleted >= 1
    assert repository.get_by_key_and_nonce(
        db_session,
        str(TEST_API_KEY_ID),
        "expired-nonce",
    ) is None
