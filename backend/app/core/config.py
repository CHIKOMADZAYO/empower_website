"""Application configuration and environment variables."""

import os
from functools import lru_cache
from pathlib import Path


class Settings:
    """Application settings from environment variables."""

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", f"sqlite:///{Path(__file__).resolve().parents[2] / 'empower.db'}"
    )

    # Security Settings
    SECRET_KEY: str = os.getenv("EMPOWER_SECRET_KEY", os.getenv("SECRET_KEY", ""))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # App Settings
    APP_NAME: str = "Empower API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "API for Empower's community-led programs and support network."
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"

    # CORS Settings
    CORS_ORIGINS: list[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = False
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings."""
    settings = Settings()
    secret_key = settings.SECRET_KEY
    if len(secret_key.encode("utf-8")) < 32 or any(
        marker in secret_key.lower() for marker in ("change-me", "development-only")
    ):
        raise ValueError("Set EMPOWER_SECRET_KEY or SECRET_KEY to at least 32 random characters.")
    return settings
