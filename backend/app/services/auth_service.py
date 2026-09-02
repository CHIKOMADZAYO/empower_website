"""Authentication service - business logic for auth operations."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.schemas.auth import SignupRequest, TokenResponse


class AuthService:
    """Business logic for authentication."""

    @staticmethod
    def authenticate_user(
        database: Session,
        username: str,
        password: str
    ) -> User | None:
        """Authenticate user with username and password."""
        user = database.scalar(
            select(User).where(User.username == username)
        )
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def create_user(
        database: Session,
        signup_request: SignupRequest
    ) -> User:
        """Create new user account."""
        # Check if username or email already exists
        existing = database.scalar(
            select(User).where(
                (User.username == signup_request.username) |
                (User.email == signup_request.email)
            )
        )
        if existing:
            raise ValueError("Username or email already exists")

        # Create new user
        user = User(
            username=signup_request.username,
            email=signup_request.email,
            hashed_password=hash_password(signup_request.password),
            role="viewer",
        )
        database.add(user)
        database.commit()
        database.refresh(user)
        return user

    @staticmethod
    def get_token_response(user: User) -> TokenResponse:
        """Generate token response for user."""
        return TokenResponse(access_token=create_access_token(user))
