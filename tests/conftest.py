import os
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.core.database
import app.core.dependencies
import app.main
import app.models
import app.services.algorithm_service
import app.services.api_key_service
import app.services.api_nonce_service
import app.services.api_security_event_service
import app.services.api_usage_service
import app.services.audit_log_service
import app.services.pqc_operation_service
from app.core.config import settings
from app.core.database import Base
from app.models.algorithm import Algorithm
from app.models.api_key import ApiKey
from app.models.user import User
from app.utils.crypto import sha256_hex

TEST_USER_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
TEST_API_KEY_ID = uuid.UUID("22222222-2222-2222-2222-222222222222")
TEST_API_KEY = "qnnx_test_key"
TEST_SIGNING_SECRET = "qnnxsig_test_secret"


@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"


@compiles(UUID, "sqlite")
def compile_uuid_sqlite(type_, compiler, **kw):
    return "VARCHAR(36)"


@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        execution_options={
            "schema_translate_map": {
                "public": None,
                "crypto": None,
                "analytics": None,
                "audit": None,
            }
        },
    )
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture(scope="session")
def testing_session_local(db_engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=db_engine)


@pytest.fixture(scope="session", autouse=True)
def patch_database(testing_session_local):
    modules = (
        app.core.database,
        app.core.dependencies,
        app.services.algorithm_service,
        app.services.api_key_service,
        app.services.api_nonce_service,
        app.services.api_security_event_service,
        app.services.api_usage_service,
        app.services.audit_log_service,
        app.services.pqc_operation_service,
    )
    originals = [(module, module.SessionLocal) for module in modules]
    for module in modules:
        module.SessionLocal = testing_session_local

    original_guard = settings.DISABLE_SIGNED_REQUEST_GUARDS
    settings.DISABLE_SIGNED_REQUEST_GUARDS = True
    yield
    settings.DISABLE_SIGNED_REQUEST_GUARDS = original_guard
    for module, original in originals:
        module.SessionLocal = original


@pytest.fixture(scope="session", autouse=True)
def seed_database(testing_session_local, patch_database):
    db = testing_session_local()
    db.add(
        User(
            id=TEST_USER_ID,
            full_name="Test User",
            role="user",
            organization_name="QNNX Test",
        )
    )
    db.add_all(
        [
            Algorithm(
                algo_id="ml-kem-768",
                name="ML-KEM-768",
                type="KEM",
                security_level="NIST Level 3",
                nist_standard="FIPS 203",
                status="active",
            ),
            Algorithm(
                algo_id="ml-dsa-65",
                name="ML-DSA-65",
                type="Signature",
                security_level="NIST Level 3",
                nist_standard="FIPS 204",
                status="active",
            ),
        ]
    )
    db.add(
        ApiKey(
            id=TEST_API_KEY_ID,
            user_id=TEST_USER_ID,
            key_prefix=TEST_API_KEY[:12],
            key_hash=sha256_hex(TEST_API_KEY),
            signing_secret_hash=sha256_hex(TEST_SIGNING_SECRET),
            name="Test Suite Key",
            status="active",
        )
    )
    db.commit()
    db.close()


@pytest.fixture()
def db_session(testing_session_local, seed_database):
    db = testing_session_local()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def client(seed_database):
    with TestClient(app.main.app) as test_client:
        yield test_client


@pytest.fixture()
def api_headers():
    return {
        "Authorization": f"Bearer {TEST_API_KEY}",
        "Content-Type": "application/json",
    }


@pytest.fixture()
def user_headers():
    return {"Authorization": f"Bearer {TEST_USER_ID}"}


def pytest_collection_modifyitems(config, items):
    if os.getenv("RUN_INTEGRATION_TESTS") == "1":
        return
    marker = pytest.mark.skip(reason="Set RUN_INTEGRATION_TESTS=1 to run external integration tests")
    for item in items:
        if "external_integration" in item.keywords:
            item.add_marker(marker)
