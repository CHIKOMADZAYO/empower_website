"""Project routes."""
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_roles
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectResponse
from app.services.project_service import ProjectService


router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectResponse])
async def list_projects(
    database: Annotated[Session, Depends(get_db)],
) -> list[ProjectResponse]:
    """Get all projects."""
    projects = ProjectService.get_all_projects(database)
    return [ProjectResponse.model_validate(p) for p in projects]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    database: Annotated[Session, Depends(get_db)],
) -> ProjectResponse:
    """Get project by ID."""
    project = ProjectService.get_project_by_id(database, project_id)
    if not project:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse.model_validate(project)


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    database: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles("admin"))],
) -> ProjectResponse:
    """Create new project."""
    new_project = ProjectService.create_project(database, project)
    return ProjectResponse.model_validate(new_project)

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project: ProjectCreate,
    database: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles("admin"))],
) -> ProjectResponse:
    """Update project by ID."""
    updated_project = ProjectService.update_project(database, project_id, project)
    if not updated_project:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectResponse.model_validate(updated_project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    database: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles("admin"))],
) -> None:
    """Delete project by ID."""
    ProjectService.delete_project(database, project_id)


