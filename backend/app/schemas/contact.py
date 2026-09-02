"""Contact message schemas - request/response models."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ContactMessageCreate(BaseModel):
    """Contact message creation schema."""
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    message: str = Field(min_length=10, max_length=2000)


class ContactMessageResponse(BaseModel):
    """Contact message response schema."""
    message: str
    received_at: datetime


class ContactMessageListResponse(BaseModel):
    """Contact message list item schema."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    message: str
    created_at: datetime
