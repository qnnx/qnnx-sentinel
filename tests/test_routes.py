from app.models.api_key import ApiKey
from tests.conftest import TEST_API_KEY_ID


def test_public_routes(client):
    assert client.get("/").status_code == 200
    assert client.get("/api/v1/health").status_code == 200
    algorithms = client.get("/api/v1/algorithms")
    assert algorithms.status_code == 200
    assert algorithms.json()["total"] == 2
    assert client.get("/api/v1/algorithms/ML-KEM-768").status_code == 200


def test_protected_crypto_routes(client, api_headers):
    keygen = client.post(
        "/api/v1/keygen",
        json={"algorithm": "ML-KEM-768", "storage_mode": "customer_managed"},
        headers=api_headers,
    )
    assert keygen.status_code == 200, keygen.text
    keys = keygen.json()

    encapsulated = client.post(
        "/api/v1/kem/encapsulate",
        json={"algorithm": "ML-KEM-768", "public_key": keys["public_key"]},
        headers=api_headers,
    )
    assert encapsulated.status_code == 200, encapsulated.text
    decapsulated = client.post(
        "/api/v1/kem/decapsulate",
        json={
            "algorithm": "ML-KEM-768",
            "ciphertext": encapsulated.json()["ciphertext"],
            "private_key": keys["private_key"],
        },
        headers=api_headers,
    )
    assert decapsulated.status_code == 200, decapsulated.text
    assert decapsulated.json()["shared_secret"] == encapsulated.json()["shared_secret"]

    dsa_keys = client.post(
        "/api/v1/keygen",
        json={"algorithm": "ML-DSA-65", "storage_mode": "customer_managed"},
        headers=api_headers,
    ).json()
    signed = client.post(
        "/api/v1/sign",
        json={
            "algorithm": "ML-DSA-65",
            "message": "route test",
            "private_key": dsa_keys["private_key"],
        },
        headers=api_headers,
    )
    assert signed.status_code == 200, signed.text
    verified = client.post(
        "/api/v1/verify",
        json={
            "algorithm": "ML-DSA-65",
            "message": "route test",
            "signature": signed.json()["signature"],
            "public_key": dsa_keys["public_key"],
        },
        headers=api_headers,
    )
    assert verified.status_code == 200, verified.text
    assert verified.json()["is_valid"] is True


def test_management_usage_and_audit_routes(client, user_headers, db_session):
    created = client.post(
        "/api/v1/api-keys",
        json={"name": "Route Test Key"},
        headers=user_headers,
    )
    assert created.status_code == 200, created.text
    payload = created.json()
    assert payload["api_key"]
    assert payload["signing_secret"]
    assert "key_hash" not in payload
    assert client.get("/api/v1/api-keys", headers=user_headers).status_code == 200

    revoked = client.post(
        "/api/v1/api-keys/revoke",
        json={"api_key_id": payload["id"]},
        headers=user_headers,
    )
    assert revoked.status_code == 200, revoked.text
    assert revoked.json()["is_active"] is False

    for path in (
        "/api/v1/api-usage",
        "/api/v1/api-usage/recent",
        "/api/v1/api-usage/summary",
        "/api/v1/audit-logs",
    ):
        response = client.get(path, headers=user_headers)
        assert response.status_code == 200, f"{path}: {response.text}"

    original_key = db_session.get(ApiKey, TEST_API_KEY_ID)
    db_session.refresh(original_key)
    assert original_key.last_used_at is not None


def test_invalid_api_key_is_rejected(client):
    response = client.post(
        "/api/v1/keygen",
        json={"algorithm": "ML-KEM-768"},
        headers={"Authorization": "Bearer invalid"},
    )
    assert response.status_code == 401
