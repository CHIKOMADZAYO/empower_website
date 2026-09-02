"""Application configuration and environment variables."""
import os
from functools import lru_cache
from pathlib import Path


class Settings:
    """Application settings from environment variables."""

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{Path(__file__).resolve().parent.parent / 'empower.db'}"
    )

    # Security
    SECRET_KEY: str = os.getenv("EMPOWER_SECRET_KEY", "development-only-change-me")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # App
    APP_NAME: str = "Empower API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "API for Empower's community-led programs and support network."
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # CORS
    CORS_ORIGINS: list[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = False
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
