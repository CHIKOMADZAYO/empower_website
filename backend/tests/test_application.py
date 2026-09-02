"""Tests for application startup and database lifecycle helpers."""

from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import create_app


def test_application_lifespan_initializes_and_seeds_database() -> None:
    """Application startup should create tables and seed empty collections."""
    with TestClient(create_app()) as application:
        projects = application.get("/api/v1/projects")
        stories = application.get("/api/v1/stories")

    assert projects.status_code == 200
    assert len(projects.json()) == 3
    assert stories.status_code == 200
    assert len(stories.json()) == 3


def test_database_dependency_yields_and_closes_session() -> None:
    """Database dependency should provide a usable session and clean it up."""
    database_generator = get_db()
    database = next(database_generator)

    assert database.is_active
    database_generator.close()
    assert database.is_active