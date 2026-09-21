"""User service - business logic for user operations."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserService:
    """Business logic for users."""

    @staticmethod
    def get_all_users(database: Session) -> list[User]:
        """Get all users ordered by ID."""
        return database.scalars(
            select(User).order_by(User.id)
        ).all()