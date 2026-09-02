"""Test module for authentication endpoints."""
from fastapi.testclient import TestClient


def test_signup_creates_user_and_returns_token(client: TestClient) -> None:
    """Test user signup creates account and returns token."""
    username = "newsignupuser"
    email = "newsignupuser@example.com"
    password = "StrongPass123"

    response = client.post(
        "/api/v1/auth/signup",
        json={"username": username, "email": email, "password": password},
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

    # Try login with non-existent user
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "nonexistent", "password": "SomePass123"},
    )
    assert response.status_code == 401
