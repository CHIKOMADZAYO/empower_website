"""User management routes."""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_roles
from app.models.user import User
from app.schemas.user import UserListResponse
from app.services.user_service import UserService


router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserListResponse])
async def list_users(
    database: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles("admin"))],
) -> list[UserListResponse]:
    """Get all users (admin only)."""
    users = UserService.get_all_users(database)
    return [UserListResponse.model_validate(user) for user in users]