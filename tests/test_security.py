import pytest
import hashlib

# 1. Import the actual class from your repo file
from app.repositories.api_key_repo import APIKeyRepository
from app.core.dependencies import _serialize_api_key


try:
    from tests.conftest import db_session, db_engine
except ImportError:
    pass

def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def test_api_key_hashing_and_database_retrieval_success(db_session):
    """Verify plaintext API tokens correctly hash and resolve against the persistent datastore lookup."""
    plaintext_key = "testkey1"
    hashed_key = sha256_hex(plaintext_key)
    
    # 2. Initialize the repository class, just like your boss's script!
    repo = APIKeyRepository()
    record = repo.get_by_hash(db_session, hashed_key)
    
    assert record is not None
    assert record.is_active == "active" 
    assert record.name == "Test Suite Key"

def test_api_key_serialization_pydantic_fallback_protection(db_session):
    """Verify that serialization successfully handles NULL key_prefixes without throwing ValidationErrors."""
    plaintext_key = "testkey1"
    
    # Initialize the repository class here as well
    repo = APIKeyRepository()
    record = repo.get_by_hash(db_session, sha256_hex(plaintext_key))
    
    # Force mock database column state to None to emulate Supabase test key configurations
    record.key_prefix = None 
    
    context = _serialize_api_key(record)
    
    assert context.key_prefix == "", "Fallback guard failed to substitute an empty string for NULL property"
    assert context.is_active is True