"""Story routes."""
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
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
) -> StoryResponse:
    """Create new community story."""
    new_story = StoryService.create_story(database, story)
    return StoryResponse.model_validate(new_story)
