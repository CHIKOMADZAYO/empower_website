"""Test configuration and fixtures."""
import sys
from pathlib import Path

# Add backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from sqlalchemy.orm import Session

from app.core.database import Base, SessionLocal, engine
from app.main import create_app
from fastapi.testclient import TestClient


@pytest.fixture(scope="function", autouse=True)
def setup_test_db():
    """Create test database and tables."""
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
