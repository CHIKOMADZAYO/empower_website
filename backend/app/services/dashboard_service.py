"""Dashboard service - aggregated read models for dashboards."""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.contact import ContactMessage
from app.models.project import Project
from app.models.story import Story
from app.models.user import User


def _count_by_field(rows: list[tuple[str | None, int]]) -> dict[str, int]:
    result: dict[str, int] = {}
    for key, count in rows:
        result[key or "Uncategorised"] = int(count)
    return result


class DashboardService:
    """Business logic for dashboard summaries."""

    @staticmethod
    def admin_summary(database: Session) -> dict:
        total_users = database.scalar(select(func.count(User.id))) or 0
        total_projects = database.scalar(select(func.count(Project.id))) or 0
        total_stories = database.scalar(select(func.count(Story.id))) or 0
        total_messages = database.scalar(select(func.count(ContactMessage.id))) or 0

        users_by_role = _count_by_field(
            list(database.execute(select(User.role, func.count(User.id)).group_by(User.role)).all())
        )
        projects_by_category = _count_by_field(
            list(database.execute(select(Project.category, func.count(Project.id)).group_by(Project.category)).all())
        )
        stories_by_category = _count_by_field(
            list(database.execute(select(Story.category, func.count(Story.id)).group_by(Story.category)).all())
        )

        recent_users = database.scalars(select(User).order_by(User.id.desc()).limit(5)).all()
        recent_projects = database.scalars(select(Project).order_by(Project.id.desc()).limit(5)).all()
        recent_stories = database.scalars(select(Story).order_by(Story.id.desc()).limit(5)).all()
        recent_messages = database.scalars(
            select(ContactMessage).order_by(ContactMessage.created_at.desc()).limit(5)
        ).all()

        return {
            "total_users": total_users,
            "total_projects": total_projects,
            "total_stories": total_stories,
            "total_messages": total_messages,
            "users_by_role": users_by_role,
            "projects_by_category": projects_by_category,
            "stories_by_category": stories_by_category,
            "recent_users": [
                {"id": u.id, "username": u.username, "email": u.email, "role": u.role} for u in recent_users
            ],
            "recent_projects": [
                {"id": p.id, "name": p.name, "category": p.category, "summary": p.summary}
                for p in recent_projects
            ],
            "recent_stories": [
                {"id": s.id, "title": s.title, "category": s.category, "year": s.year} for s in recent_stories
            ],
            "recent_messages": [
                {
                    "id": m.id,
                    "name": m.name,
                    "email": m.email,
                    "message": m.message[:140],
                    "created_at": m.created_at.isoformat() if m.created_at else None,
                }
                for m in recent_messages
            ],
        }

    @staticmethod
    def user_summary(database: Session, user: User) -> dict:
        total_projects = database.scalar(select(func.count(Project.id))) or 0
        total_stories = database.scalar(select(func.count(Story.id))) or 0

        my_messages = (
            database.scalars(
                select(ContactMessage)
                .where(ContactMessage.email == user.email)
                .order_by(ContactMessage.created_at.desc())
                .limit(10)
            ).all()
        )
        latest_projects = database.scalars(select(Project).order_by(Project.id.desc()).limit(6)).all()
        latest_stories = database.scalars(select(Story).order_by(Story.id.desc()).limit(6)).all()

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "total_projects": total_projects,
            "total_stories": total_stories,
            "my_messages": [
                {
                    "id": m.id,
                    "name": m.name,
                    "message": m.message,
                    "created_at": m.created_at.isoformat() if m.created_at else None,
                }
                for m in my_messages
            ],
            "latest_projects": [
                {"id": p.id, "name": p.name, "category": p.category, "summary": p.summary}
                for p in latest_projects
            ],
            "latest_stories": [
                {
                    "id": s.id,
                    "title": s.title,
                    "category": s.category,
                    "excerpt": s.excerpt,
                    "year": s.year,
                }
                for s in latest_stories
            ],
        }
