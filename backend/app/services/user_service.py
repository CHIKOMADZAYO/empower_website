"""User service - business logic for user operations."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
# from app.schemas.user import UserUpdate



class UserService:
    """Business logic for users."""

    @staticmethod
    def get_all_users(database: Session) -> list[User]:
        """Get all users ordered by ID."""
        return database.scalars(
            select(User).order_by(User.id)
        ).all()
        
    @staticmethod
    def get_user(database:Session,user_id:int)->User:
        return database.scalars(
            select(User).where(User.id==user_id)
        ).first()
        
    @staticmethod
    def update_user(database:Session,user_data:User):
        # Check the User if exist first
        user=UserService.get_user(database,user_data.id)
        if not user:
            return f"User of id {user_data.id}"
        
        for key, value in user_data.model_dump().items():
            setattr(user, key, value)
        database.commit()
        database.refresh(user)
        
        return user
            