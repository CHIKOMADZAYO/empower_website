"""Authentication schemas - request/response models."""
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Login request schema."""
    username: str = Field(min_length=2, max_length=100)
    password: str = Field(min_length=8, max_length=128)


class SignupRequest(BaseModel):
    """Signup request schema."""
    username: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    """Authentication token response schema."""
    access_token: str
    token_type: str = "bearer"
