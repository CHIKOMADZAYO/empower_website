"""Test module for authentication endpoints."""

from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.core.roles import UserRole
from app.core.security import create_access_token, hash_password
from app.models.log_activity import ActivityLog
from app.models.user import User


def test_signup_creates_user_and_returns_token(client: TestClient) -> None:
    """Test user signup creates account and returns token."""
    username = "newsignupuser"
    email = "newsignupuser@example.com"
    password = "StrongPass123"

    response = client.post(
        "/api/v1/auth/signup",
        json={"username": username, "email": email, "password": password, "role": "admin"},
    )

    assert response.status_code == 201, response.text
    payload = response.json()
    assert "access_token" in payload
    assert payload["token_type"] == "bearer"

    # Verify login works with same credentials
    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert login_response.status_code == 200, login_response.text

    with SessionLocal() as database:
        user = database.query(User).filter(User.username == username).one()
        assert user.role == UserRole.VIEWER
        actions = (
            database.query(ActivityLog.action)
            .filter(ActivityLog.user_id == user.id)
            .order_by(ActivityLog.id)
            .all()
        )

    assert [action for (action,) in actions] == ["USER_SIGNUPS", "USER_LOGINS"]


def test_signup_with_existing_username_or_email_fails(client: TestClient) -> None:
    """Test signup fails when username or email already exists."""
    # Create first user
    client.post(
        "/api/v1/auth/signup",
        json={
            "username": "existinguser",
            "email": "existing@example.com",
            "password": "StrongPass123",
        },
    )

    # Try to sign up with same username
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "username": "existinguser",
            "email": "different@example.com",
            "password": "StrongPass123",
        },
    )
    assert response.status_code == 409

    # Try to sign up with same email
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "username": "differentuser",
            "email": "existing@example.com",
            "password": "StrongPass123",
        },
    )
    assert response.status_code == 409


def test_login_with_incorrect_credentials_fails(client: TestClient) -> None:
    """Test login fails with incorrect credentials."""
    # Create user
    client.post(
        "/api/v1/auth/signup",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "CorrectPass123",
        },
    )

    # Try login with wrong password
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "WrongPass123"},
    )
    assert response.status_code == 401


def test_bootstrap_admin_creates_first_admin_once(
    client: TestClient, monkeypatch
) -> None:
    """Only a valid bootstrap token can create the first admin user."""
    monkeypatch.setenv("ADMIN_BOOTSTRAP_TOKEN", "bootstrap-secret-123456")

    response = client.post(
        "/api/v1/auth/bootstrap-admin",
        json={
            "username": "bootstrapadmin",
            "email": "bootstrapadmin@example.com",
            "password": "StrongPass123",
            "bootstrap_token": "bootstrap-secret-123456",
        },
    )

    assert response.status_code == 201, response.text
    payload = response.json()
    assert "access_token" in payload

    with SessionLocal() as database:
        user = database.query(User).filter(User.username == "bootstrapadmin").one()
        assert user.role == UserRole.ADMIN

    second_response = client.post(
        "/api/v1/auth/bootstrap-admin",
        json={
            "username": "anotheradmin",
            "email": "anotheradmin@example.com",
            "password": "StrongPass123",
            "bootstrap_token": "bootstrap-secret-123456",
        },
    )
    assert second_response.status_code == 409, second_response.text


def test_unexpected_errors_are_sanitized(client: TestClient, monkeypatch) -> None:
    """Unexpected exceptions should not leak internals to API clients."""

    def boom(*args, **kwargs):
        raise RuntimeError("database password leak: secret-admin-pw")

    monkeypatch.setattr("app.services.auth_service.AuthService.authenticate_user", staticmethod(boom))

    response = client.post(
        "/api/v1/auth/login",
        json={"username": "anyuser", "password": "StrongPass123"},
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
    assert "secret-admin-pw" not in response.text


def test_inactive_user_cannot_login_or_use_existing_token(client: TestClient) -> None:
    """Deactivated accounts are rejected by both login and token authentication."""
    with SessionLocal() as database:
        user = User(
            username="inactiveuser",
            email="inactiveuser@example.com",
            hashed_password=hash_password("StrongPass123"),
            role=UserRole.VIEWER,
            is_active=False,
        )
        database.add(user)
        database.commit()
        database.refresh(user)
        token = create_access_token(user)

    login_response = client.post(
        "/api/v1/auth/login",
        json={"username": "inactiveuser", "password": "StrongPass123"},
    )
    assert login_response.status_code == 401, login_response.text

    profile_response = client.get(
        "/api/v1/auth/profile",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert profile_response.status_code == 401, profile_response.text

    # Try login with non-existent user
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "nonexistent", "password": "SomePass123"},
    )
    assert response.status_code == 401
