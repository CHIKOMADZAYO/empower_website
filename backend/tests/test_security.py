"""Tests for authentication and security utilities."""

from datetime import datetime, timedelta, timezone

import jwt
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.core.security import (
    create_access_token,
    hash_password,
    public_user,
    require_roles,
    verify_password,
)
from app.models.user import User


def test_password_hashing_round_trip() -> None:
    """Passwords should verify only against their matching hash."""
    hashed = hash_password("StrongPass123")

    assert hashed != "StrongPass123"
    assert verify_password("StrongPass123", hashed)
    assert not verify_password("WrongPass123", hashed)


def test_profile_returns_public_user_without_password(client: TestClient) -> None:
    """An authenticated user can read a safe public profile."""
    signup = client.post(
        "/api/v1/auth/signup",
        json={
            "username": "profileuser",
            "email": "profile@example.com",
            "password": "StrongPass123",
        },
    )
    token = signup.json()["access_token"]

    response = client.get(
        "/api/v1/auth/profile",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Authenticated as profileuser",
        "user": {"id": 1, "username": "profileuser", "role": "viewer"},
    }
    assert "hashed_password" not in response.json()["user"]


def test_profile_rejects_invalid_expired_and_unknown_tokens(client: TestClient) -> None:
    """Profile access should reject unusable bearer tokens."""
    settings = get_settings()
    expired = jwt.encode(
        {"sub": "1", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    unknown_user = jwt.encode(
        {"sub": "9999", "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    for token in ("not-a-token", expired, unknown_user):
        response = client.get(
            "/api/v1/auth/profile",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 401


def test_security_helpers_create_token_and_public_user(test_db) -> None:
    """Security helpers should encode identity and omit private fields."""
    user = User(
        username="helperuser",
        email="helper@example.com",
        hashed_password=hash_password("StrongPass123"),
        role="admin",
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    token = create_access_token(user)
    payload = jwt.decode(
        token,
        get_settings().SECRET_KEY,
        algorithms=[get_settings().ALGORITHM],
    )
    public = public_user(user)

    assert payload["sub"] == str(user.id)
    assert payload["username"] == "helperuser"
    assert payload["role"] == "admin"
    assert public.model_dump() == {"id": user.id, "username": "helperuser", "role": "admin"}


def test_require_roles_allows_matching_role_and_rejects_other_role() -> None:
    """Role dependency should enforce its allowed role list."""
    dependency = require_roles("admin")
    admin = User(username="admin", email="admin@example.com", hashed_password="hash", role="admin")
    viewer = User(username="viewer", email="viewer@example.com", hashed_password="hash", role="viewer")

    assert dependency(admin) is admin

    try:
        dependency(viewer)
    except Exception as error:
        assert getattr(error, "status_code", None) == 403
    else:
        raise AssertionError("viewer should not pass the admin role dependency")