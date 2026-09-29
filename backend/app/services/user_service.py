"""User service - business logic for user operations."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserService:
    """Business logic for users."""

    @staticmethod
    def get_all_users(database: Session) -> list[User]:
        """Get all users ordered by ID."""
        return list(database.scalars(select(User).order_by(User.id)).all())

    @staticmethod
    def get_user(database: Session, user_id: int) -> User | None:
        return database.scalars(select(User).where(User.id == user_id)).first()

    @staticmethod
    def update_user(database: Session, user_data: User) -> Any:
        # Check the User if exist first
        user = UserService.get_user(database, user_data.id)
        if not user:
            return f"User of id {user_data.id}"

        for key in ("username", "email", "role", "is_active"):
            value = getattr(user_data, key, None)
            if value is not None:
                setattr(user, key, value)
        database.commit()
        database.refresh(user)

        return user
