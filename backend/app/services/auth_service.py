"""Authentication service - business logic for auth operations."""
import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.mail import Mail
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.schemas.auth import SignupRequest, TokenResponse


logger = logging.getLogger(__name__)


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
    async def send_welcome_email(user: User) -> None:
        """Send a welcome email when SMTP delivery is configured."""
        settings = get_settings()
        if not settings.MAIL_ENABLED or not all(
            (settings.MAIL_USERNAME, settings.MAIL_PASSWORD, settings.MAIL_FROM, settings.MAIL_SERVER)
        ):
            return

        mail = Mail(settings)
        attempts = max(1, settings.MAIL_RETRY_ATTEMPTS)
        for attempt in range(attempts):
            try:
                await mail.send_email(
                    subject="Welcome to Empower!",
                    recipients=[user.email],
                    body=(
                        f"Hello {user.username},\n\n"
                        "Thank you for signing up for Empower! We're excited to have you on board.\n\n"
                        "Best regards,\nThe Empower Team"
                    ),
                )
                return
            except Exception:
                if attempt == attempts - 1:
                    logger.exception("Unable to send welcome email to %s", user.email)
                    return
                delay = settings.MAIL_RETRY_DELAY_SECONDS * (2**attempt)
                await asyncio.sleep(max(0, delay))


    @staticmethod
    def get_user_by_username(database: Session, username: str) -> User | None:
        """Retrieve user by username."""
        return database.scalar(
            select(User).where(User.username == username)
        )

    @staticmethod
    def get_user_by_email(database: Session, email: str) -> User | None:
        """Retrieve user by email."""
        return database.scalar(
            select(User).where(User.email == email)
        )

    @staticmethod
    def get_user_by_id(database: Session, user_id: int) -> User | None:
        """Retrieve user by ID."""
        return database.scalar(
            select(User).where(User.id == user_id)
        )
    
    @staticmethod
    def get_token_response(user: User) -> TokenResponse:
        """Generate token response for user."""
        return TokenResponse(access_token=create_access_token(user))
