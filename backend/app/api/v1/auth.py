"""Authentication routes."""
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, public_user
from app.core.task import Task
from app.models.user import User
from app.schemas.auth import LoginRequest, SignupRequest, TokenResponse
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(
    credentials: LoginRequest,
    database: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    """Authenticate user and return access token."""
    user = AuthService.authenticate_user(
        database,
        credentials.username,
        credentials.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    return AuthService.get_token_response(user)


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignupRequest,
    database: Annotated[Session, Depends(get_db)],
    background_tasks: BackgroundTasks,
) -> TokenResponse:
    """Register new user account."""
    try:
        user = AuthService.create_user(database, request)
        Task(background_tasks).add_task(AuthService.send_welcome_email, user)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    return AuthService.get_token_response(user)


@router.get("/profile")
async def get_profile(
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict:
    """Get current user profile."""
    return {
        "message": f"Authenticated as {current_user.username}",
        "user": public_user(current_user),
    }


