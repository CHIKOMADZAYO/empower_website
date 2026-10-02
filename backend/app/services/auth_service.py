"""Authentication service - business logic for auth operations."""

import hmac
import os

from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.roles import UserRole
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.auth import AdminBootstrapRequest, SignupRequest, TokenResponse


class AuthService:
    """Business logic for authentication."""

    @staticmethod
    def authenticate_user(database: Session, username: str, password: str) -> User | None:
        """Authenticate user with username and password."""
        user = database.scalar(select(User).where(User.username == username))
        if not user or not user.is_active or not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def create_user(database: Session, signup_request: SignupRequest) -> User:
        """Create new user account."""
        # Check if username or email already exists
        existing = database.scalar(
            select(User).where(
                (User.username == signup_request.username) | (User.email == signup_request.email)
            )
        )
        if existing:
            raise ValueError("Username or email already exists")

        # Create new user
        user = User(
            username=signup_request.username,
            email=signup_request.email,
            hashed_password=hash_password(signup_request.password),
            role=UserRole.VIEWER,
        )
        database.add(user)
        database.commit()
        database.refresh(user)
        return user

    @staticmethod
    def bootstrap_admin(database: Session, request: AdminBootstrapRequest) -> User:
        """Create the first admin account exactly once when a valid bootstrap token is provided."""
        bootstrap_token = os.getenv(
            "ADMIN_BOOTSTRAP_TOKEN", os.getenv("FIRST_ADMIN_BOOTSTRAP_TOKEN", "")
        )
        if not bootstrap_token:
            raise PermissionError("Admin bootstrap is disabled.")

        if not hmac.compare_digest(
            request.bootstrap_token.encode("utf-8"),
            bootstrap_token.encode("utf-8"),
        ):
            raise PermissionError("Invalid bootstrap token.")

        try:
            database.execute(text("BEGIN IMMEDIATE"))
            existing_admin = database.scalar(select(User).where(User.role == UserRole.ADMIN).limit(1))
            if existing_admin is not None:
                raise ValueError("An admin account already exists.")

            existing = database.scalar(
                select(User).where(
                    (User.username == request.username) | (User.email == request.email)
                )
            )
            if existing:
                raise ValueError("Username or email already exists")

            user = User(
                username=request.username,
                email=request.email,
                hashed_password=hash_password(request.password),
                role=UserRole.ADMIN,
            )
            database.add(user)
            database.flush()
            database.commit()
            database.refresh(user)
            return user
        except IntegrityError:
            database.rollback()
            raise ValueError("Username or email already exists") from None
        except ValueError:
            database.rollback()
            raise

    @staticmethod
    def get_token_response(user: User) -> TokenResponse:
        """Generate token response for user."""
        return TokenResponse(access_token=create_access_token(user))
