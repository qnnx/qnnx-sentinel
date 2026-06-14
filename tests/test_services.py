import pytest
from app.services.key_service import generate_keypair

def test_algorithm_lookup_service_routes_kem():
    """Verify key_service seamlessly routes KEM algorithm requests."""
    result = generate_keypair("ML-KEM-768")
    
    assert result["success"] is True
    assert "key" in result
    assert result["key"]["key_type"] == "kem"
    assert result["key"]["algorithm"] == "ML-KEM-768"
    assert "private_key_export" in result

def test_algorithm_lookup_service_routes_dsa():
    """Verify key_service seamlessly routes DSA algorithm requests."""
    result = generate_keypair("ML-DSA-65")
    
    assert result["success"] is True
    assert "key" in result
    assert result["key"]["key_type"] == "dsa"
    assert result["key"]["algorithm"] == "ML-DSA-65"

def test_algorithm_lookup_service_unsupported_fails():
    """Verify system returns clean failure dictionary objects when passed non-existent protocols."""
    result = generate_keypair("INVALID-PQC-ALGO")
    
    assert result["success"] is False
    assert "error" in result
    assert "Unsupported algorithm" in result["error"]