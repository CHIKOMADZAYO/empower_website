"""Dashboard schemas - request/response models."""

from pydantic import BaseModel, ConfigDict


class AdminSummaryResponse(BaseModel):
    """Aggregated stats for the admin dashboard."""

    total_users: int
    total_projects: int
    total_stories: int
    total_messages: int
    users_by_role: dict[str, int]
    projects_by_category: dict[str, int]
    stories_by_category: dict[str, int]
    recent_users: list[dict]
    recent_projects: list[dict]
    recent_stories: list[dict]
    recent_messages: list[dict]


class UserSummaryResponse(BaseModel):
    """Personalised summary for a logged-in (non-admin) user."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    role: str
    total_projects: int
    total_stories: int
    my_messages: list[dict]
    latest_projects: list[dict]
    latest_stories: list[dict]
