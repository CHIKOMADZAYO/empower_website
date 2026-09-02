"""Tests for request validation and error responses."""

from fastapi.testclient import TestClient


def test_auth_validation_rejects_short_and_invalid_fields(client: TestClient) -> None:
    """Auth endpoints should reject invalid request bodies."""
    short_signup = client.post(
        "/api/v1/auth/signup",
        json={"username": "a", "email": "not-an-email", "password": "short"},
    )
    assert short_signup.status_code == 422

    short_login = client.post(
        "/api/v1/auth/login",
        json={"username": "a", "password": "short"},
    )
    assert short_login.status_code == 422


def test_project_and_story_validation_rejects_incomplete_payloads(client: TestClient) -> None:
    """Project and story endpoints should enforce schema constraints."""
    project_response = client.post(
        "/api/v1/projects",
        json={"name": "x", "category": "", "summary": "x", "description": "short"},
    )
    story_response = client.post(
        "/api/v1/stories",
        json={"title": "x", "category": "Learning", "excerpt": "short"},
    )

    assert project_response.status_code == 422
    assert story_response.status_code == 422


def test_contact_validation_rejects_invalid_email_and_short_message(client: TestClient) -> None:
    """Contact submissions should enforce email and message constraints."""
    response = client.post(
        "/api/v1/contact",
        json={"name": "A", "email": "invalid", "message": "short"},
    )

    assert response.status_code == 422