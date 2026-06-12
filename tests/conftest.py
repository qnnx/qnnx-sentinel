import os
import sys
import uuid
import hashlib
import pytest
from sqlalchemy import create_engine, text, Column, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.pool import StaticPool
from app.core.database import Base

# Force a dummy DATABASE_URL string
if not os.environ.get("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

@compiles(JSONB, 'sqlite')
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"

class MockUser(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'auth', 'extend_existing': True}
    id = Column(String, primary_key=True)

@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(
        os.environ["DATABASE_URL"], 
        connect_args={"check_same_thread": False},
        poolclass=StaticPool, # Ensures memory persists across all tests
        execution_options={"schema_translate_map": {"auth": None, "crypto": None, "public": None}}
    )
    
    for table in Base.metadata.tables.values():
        for column in table.columns:
            column.server_default = None

    Base.metadata.create_all(bind=engine)
    
    #  THE FIX: Calculate the EXACT hash the test is searching for!
    test_key_hash = hashlib.sha256("testkey1".encode("utf-8")).hexdigest()
    
    # Generate robust UUIDs to satisfy database typing
    mock_api_key_id = str(uuid.uuid4())
    mock_user_id = str(uuid.uuid4())
    
    with engine.connect() as connection:
        connection.execute(text(f"INSERT OR IGNORE INTO users (id) VALUES ('{mock_user_id}')"))
        
        connection.execute(text(f"INSERT INTO algorithms (id, algo_id, name, type, security_level, nist_standard, status) VALUES ('{uuid.uuid4()}', 'algo1', 'ML-KEM-512', 'kem', 1, 'yes', 'active')"))
        connection.execute(text(f"INSERT INTO algorithms (id, algo_id, name, type, security_level, nist_standard, status) VALUES ('{uuid.uuid4()}', 'algo2', 'ML-KEM-768', 'kem', 3, 'yes', 'active')"))
        connection.execute(text(f"INSERT INTO algorithms (id, algo_id, name, type, security_level, nist_standard, status) VALUES ('{uuid.uuid4()}', 'algo3', 'ML-DSA-65', 'dsa', 3, 'yes', 'active')"))
        
        # Insert the perfectly matched hash
        connection.execute(text(f"""
            INSERT INTO api_keys (id, user_id, key_prefix, key_hash, signing_secret_hash, name, status, created_at)
            VALUES (
                '{mock_api_key_id}',
                '{mock_user_id}',
                'test',
                '{test_key_hash}',
                'dummy_secret',
                'Test Suite Key',
                'active',
                '2026-06-11 12:00:00'
            )
        """))
        connection.commit()
        
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(db_engine):
    connection = db_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()