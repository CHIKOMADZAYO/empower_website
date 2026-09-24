"""Dashboard routes - aggregated summaries for admin and normal users."""
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_roles
from app.models.user import User
from app.schemas.dashboard import AdminSummaryResponse, UserSummaryResponse
from app.services.dashboard_service import DashboardService


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/admin", response_model=AdminSummaryResponse)
async def admin_dashboard(
    database: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles("admin"))],
) -> AdminSummaryResponse:
    """Get aggregated stats for the admin dashboard (admin only)."""
    summary = DashboardService.admin_summary(database)
    return AdminSummaryResponse.model_validate(summary)


@router.get("/me", response_model=UserSummaryResponse)
async def my_dashboard(
    database: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserSummaryResponse:
    """Get personalised summary for the logged-in user."""
    summary = DashboardService.user_summary(database, current_user)
    return UserSummaryResponse.model_validate(summary)
