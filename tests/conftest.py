import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Import explicitly to avoid naming collisions with the 'app' folder
import app.main
import app.core.database
from app.core.database import Base
import app.models  # Ensures tables are registered before creating the sandbox
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import JSONB, UUID, ARRAY

# =====================================================================
# SQLite Translation Hacks for PostgreSQL Types
# =====================================================================
@compiles(JSONB, 'sqlite')
def compile_jsonb_sqlite(type_, compiler, **kw):
    # Tell SQLite to treat Postgres JSONB as a standard JSON/Text column
    return 'JSON'

@compiles(UUID, 'sqlite')
def compile_uuid_sqlite(type_, compiler, **kw):
    # Tell SQLite to treat Postgres UUIDs as standard strings
    return 'VARCHAR'

@compiles(ARRAY, 'sqlite')
def compile_array_sqlite(type_, compiler, **kw):
    # Tell SQLite to treat Postgres Arrays as standard strings
    return 'VARCHAR'
# =====================================================================
# 1. Database Engine (Restored your SQLite sandbox)
# =====================================================================
@pytest.fixture(scope="session")
def db_engine():
    # Force a dummy memory URL so local tests never touch the live DB
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    
    engine = create_engine(
        os.environ["DATABASE_URL"],
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        execution_options={
            "schema_translate_map": {
                "auth": None, 
                "crypto": None, 
                "public": None, 
                "analytics": None, # <--- Added this line!
                "audit": None      # <--- Added this just in case he used an audit schema too
            }
        }
    )
    
    for table in Base.metadata.tables.values():
        for column in table.columns:
            column.server_default = None
            
    Base.metadata.create_all(bind=engine)
    return engine

# =====================================================================
# 2. Test Client
# =====================================================================
@pytest.fixture(scope="module")
def client():
    # Explicitly use app.main.app to guarantee we get the FastAPI instance
    with TestClient(app.main.app) as c:
        yield c

# =====================================================================
# 3. Database Sandbox Protector
# =====================================================================
@pytest.fixture(scope="function", autouse=True)
def patch_database_session(db_engine):
    """Intercepts direct database imports to protect the live Supabase."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    
    original_session_local = app.core.database.SessionLocal
    original_engine = app.core.database.engine
    
    app.core.database.SessionLocal = TestingSessionLocal
    app.core.database.engine = db_engine
    
    yield
    
    app.core.database.SessionLocal = original_session_local
    app.core.database.engine = original_engine

# =====================================================================
# 4. Database Session for Assertions
# =====================================================================
@pytest.fixture(scope="function")
def db_session(db_engine):
    """Provides a session strictly for verifying database side-effects."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()