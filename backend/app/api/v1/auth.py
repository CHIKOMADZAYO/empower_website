"""Authentication routes."""

from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, public_user
from app.models.user import User
from app.schemas.auth import AdminBootstrapRequest, LoginRequest, SignupRequest, TokenResponse
from app.services.auth_service import AuthService
from app.services.logs_service import record_activity_in_background

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(
    request: Request,
    background_tasks: BackgroundTasks,
    credentials: LoginRequest,
    database: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    """Authenticate user and return access token."""
    user = AuthService.authenticate_user(database, credentials.username, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    background_tasks.add_task(
        record_activity_in_background,
        user_id=user.id,
        action="USER_LOGINS",
        resource="user",
        resource_id=str(user.id),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return AuthService.get_token_response(user)


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(
    required: Request,
    background_tasks: BackgroundTasks,
    request: SignupRequest,
    database: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    """Register new user account."""
    try:
        user = AuthService.create_user(database, request)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    # Record user signup activity
    background_tasks.add_task(
        record_activity_in_background,
        user_id=user.id,
        action="USER_SIGNUPS",
        resource="user",
        resource_id=str(user.id),
        ip_address=required.client.host if required.client else None,
        user_agent=required.headers.get("user-agent"),
    )

    return AuthService.get_token_response(user)


@router.post("/bootstrap-admin", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def bootstrap_admin(
    http_request: Request,
    background_tasks: BackgroundTasks,
    request: AdminBootstrapRequest,
    database: Annotated[Session, Depends(get_db)],
) -> TokenResponse:
    """Create the first admin account using a one-time bootstrap secret."""
    try:
        user = AuthService.bootstrap_admin(database, request)
    except PermissionError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        ) from error
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    background_tasks.add_task(
        record_activity_in_background,
        user_id=user.id,
        action="ADMIN_BOOTSTRAP",
        resource="user",
        resource_id=str(user.id),
        ip_address=http_request.client.host if http_request.client else None,
        user_agent=http_request.headers.get("user-agent"),
    )
    return AuthService.get_token_response(user)


@router.get("/profile")
def get_profile(
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict:
    """Get current user profile."""
    return {
        "message": f"Authenticated as {current_user.username}",
        "user": public_user(current_user),
    }
