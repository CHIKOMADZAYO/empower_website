"""Project schemas - request/response models."""
from pydantic import BaseModel, ConfigDict, Field


class ProjectBase(BaseModel):
    """Base project schema."""
    name: str = Field(min_length=2, max_length=100)
    category: str = Field(min_length=2, max_length=100)
    summary: str = Field(min_length=2, max_length=255)
    description: str = Field(min_length=10, max_length=2000)


class ProjectCreate(ProjectBase):
    """Project creation schema."""
    pass


class ProjectResponse(ProjectBase):
    """Project response schema."""
    model_config = ConfigDict(from_attributes=True)

    id: int
