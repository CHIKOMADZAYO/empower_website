"""Story schemas - request/response models."""
from pydantic import BaseModel, ConfigDict, Field


class StoryBase(BaseModel):
    """Base story schema."""
    title: str = Field(min_length=2, max_length=255)
    category: str = Field(min_length=2, max_length=100)
    excerpt: str = Field(min_length=10, max_length=2000)
    year: int


class StoryCreate(StoryBase):
    """Story creation schema."""
    pass


class StoryResponse(StoryBase):
    """Story response schema."""
    model_config = ConfigDict(from_attributes=True)

    id: int
