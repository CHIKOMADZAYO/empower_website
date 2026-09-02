"""User schemas - request/response models."""
from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    """Base user schema."""
    username: str = Field(min_length=2, max_length=100)
    role: str


class UserResponse(UserBase):
    """User response schema."""
    model_config = ConfigDict(from_attributes=True)

    id: int
