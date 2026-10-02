"""Test configuration and fixtures."""

import os
import sys
import tempfile
from pathlib import Path

# Add backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ.setdefault("EMPOWER_SECRET_KEY", "test-only-secret-key-with-at-least-32-bytes")

# Never let destructive test fixtures connect to the developer's application DB.
test_database_url = os.environ.get("EMPOWER_TEST_DATABASE_URL")
if test_database_url:
    os.environ["EMPOWER_TEST_DATABASE_URL"] = test_database_url
else:
    test_database = tempfile.NamedTemporaryFile(prefix="empower-test-", suffix=".db", delete=False)
    test_database.close()
    os.environ["EMPOWER_TEST_DATABASE_URL"] = f"sqlite:///{test_database.name}"

import pytest
from fastapi.testclient import TestClient

from app.core.database import Base, SessionLocal, engine
from app.main import create_app


@pytest.fixture(scope="function", autouse=True)
def setup_test_db():
    """Reset the database to an empty state before each test."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_db():
    """Get test database session."""
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client():
    """Get test client."""
    app = create_app()
    return TestClient(app)
