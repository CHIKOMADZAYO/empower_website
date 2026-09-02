"""Story service - business logic for story operations."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.story import Story
from app.schemas.story import StoryCreate, StoryResponse


class StoryService:
    """Business logic for stories."""

    @staticmethod
    def get_all_stories(database: Session) -> list[Story]:
        """Get all stories."""
        return database.scalars(
            select(Story).order_by(Story.id)
        ).all()

    @staticmethod
    def get_story_by_id(database: Session, story_id: int) -> Story | None:
        """Get story by ID."""
        return database.scalar(
            select(Story).where(Story.id == story_id)
        )

    @staticmethod
    def create_story(
        database: Session,
        story_data: StoryCreate
    ) -> Story:
        """Create new story."""
        story = Story(**story_data.model_dump())
        database.add(story)
        database.commit()
        database.refresh(story)
        return story


    @staticmethod
    def update_story(
        database: Session,
        story_id: int,
        story_data: StoryCreate
    ) -> Story | None:
        """Update story by ID."""
        story = database.scalar(
            select(Story).where(Story.id == story_id)
        )
        if not story:
            return None
        for key, value in story_data.model_dump().items():
            setattr(story, key, value)
        database.commit()
        database.refresh(story)
        return story


    @staticmethod
    def delete_story(database: Session, story_id: int) -> None:
        """Delete story by ID."""
        story = database.scalar(
            select(Story).where(Story.id == story_id)
        )
        if  not story:
            return {
                "message": "Story not found",
                "status_code": 404
            }
        database.delete(story)
        database.commit()