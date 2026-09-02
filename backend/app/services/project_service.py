"""Project service - business logic for project operations."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectResponse


class ProjectService:
    """Business logic for projects."""

    @staticmethod
    def get_all_projects(database: Session) -> list[Project]:
        """Get all projects."""
        return database.scalars(
            select(Project).order_by(Project.id)
        ).all()

    @staticmethod
    def get_project_by_id(database: Session, project_id: int) -> Project | None:
        """Get project by ID."""
        return database.scalar(
            select(Project).where(Project.id == project_id)
        )

    @staticmethod
    def create_project(
        database: Session,
        project_data: ProjectCreate
    ) -> Project:
        """Create new project."""
        project = Project(**project_data.model_dump())
        database.add(project)
        database.commit()
        database.refresh(project)
        return project

    @staticmethod
    def update_project(
        database: Session,
        project_id: int,
        project_data: ProjectCreate
    ) -> Project | None:
        """Update project by ID."""
        project = database.scalar(
            select(Project).where(Project.id == project_id)
        )
        if not project:
            return None
        for key, value in project_data.model_dump().items():
            setattr(project, key, value)
        database.commit()
        database.refresh(project)
        return project


    @staticmethod
    def delete_project(database: Session, project_id: int) -> None:
        """Delete project by ID."""
        project = database.scalar(
            select(Project).where(Project.id == project_id)
        )
        if project:
            database.delete(project)
            database.commit()