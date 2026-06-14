import pytest
from fastapi import HTTPException

from app.services.key_service import generate_keypair


def test_key_service_routes_supported_algorithms():
    kem = generate_keypair("ML-KEM-768")
    signature = generate_keypair("ML-DSA-65")
    assert kem["key_type"] == "kem"
    assert signature["key_type"] == "dsa"
    assert kem["private_key"]
    assert signature["private_key"]


def test_key_service_rejects_unsupported_algorithm():
    with pytest.raises(HTTPException) as exc_info:
        generate_keypair("INVALID-PQC-ALGO")
    assert exc_info.value.status_code == 400
