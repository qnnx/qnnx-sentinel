import os
from urllib.parse import urlparse

import pytest


def _validated_test_database_url() -> str:
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL is required for external integration tests")

    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    database = parsed.path.rsplit("/", 1)[-1].lower()
    if "supabase" in host or "pooler.supabase.com" in host:
        pytest.fail("External integration tests cannot run against Supabase")
    if "test" not in database:
        pytest.fail("TEST_DATABASE_URL database name must contain 'test'")
    return url


@pytest.mark.external_integration
def test_external_database_guard():
    assert _validated_test_database_url().startswith(("postgresql://", "postgresql+psycopg2://"))
