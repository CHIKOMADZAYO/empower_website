"""Story routes."""
from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_roles
from app.models.user import User
from app.schemas.story import StoryCreate, StoryResponse
from app.services.story_service import StoryService


router = APIRouter(prefix="/stories", tags=["stories"])


@router.get("", response_model=list[StoryResponse])
async def list_stories(
    database: Annotated[Session, Depends(get_db)],
) -> list[StoryResponse]:
    """Get all community stories."""
    stories = StoryService.get_all_stories(database)
    return [StoryResponse.model_validate(s) for s in stories]


@router.get("/{story_id}", response_model=StoryResponse)
async def get_story(
    story_id: int,
    database: Annotated[Session, Depends(get_db)],
) -> StoryResponse:
    """Get story by ID."""
    story = StoryService.get_story_by_id(database, story_id)
    if not story:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Story not found")
    return StoryResponse.model_validate(story)


@router.post("", response_model=StoryResponse, status_code=status.HTTP_201_CREATED)
async def create_story(
    story: StoryCreate,
    database: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles("admin"))],
) -> StoryResponse:
    """Create new community story."""
    new_story = StoryService.create_story(database, story)
    return StoryResponse.model_validate(new_story)


@router.delete("/{story_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_story( 
    story_id: int,
    database: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles("admin"))],
) -> None:
    """Delete community story by ID."""
    StoryService.delete_story(database, story_id)


@router.put("/{story_id}", response_model=StoryResponse)
async def update_story(
    story_id: int,
    story: StoryCreate,
    database: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_roles("admin"))],
) -> StoryResponse:
    """Update community story by ID."""
    updated_story = StoryService.update_story(database, story_id, story)
    if not updated_story:
        raise HTTPException(status_code=404, detail="Story not found")
    return StoryResponse.model_validate(updated_story)

