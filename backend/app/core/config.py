"""Application configuration and environment variables."""
import os
from functools import lru_cache
from pathlib import Path



   

class Settings:
    """Application settings from environment variables."""

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{Path(__file__).resolve().parents[2] / 'empower.db'}"
    )

    # Security Settings
    SECRET_KEY: str = os.getenv(
        "EMPOWER_SECRET_KEY",
        "development-only-change-me-32-bytes-minimum",
    )
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

    #Email Configurations
    # Email configuration. Email is disabled until credentials are provided.
    MAIL_USERNAME: str = os.getenv("EMAIL_USERNAME", "")
    MAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", "")
    MAIL_FROM: str = os.getenv("EMAIL_FROM", MAIL_USERNAME)
    MAIL_PORT: int = int(os.getenv("EMAIL_PORT", "587"))
    MAIL_SERVER: str = os.getenv("EMAIL_HOST", "")
    MAIL_STARTTLS: bool = os.getenv("EMAIL_STARTTLS", "true").lower() == "true"
    MAIL_SSL_TLS: bool = os.getenv("EMAIL_SSL_TLS", "false").lower() == "true"
    MAIL_ENABLED: bool = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
    MAIL_RETRY_ATTEMPTS: int = int(os.getenv("EMAIL_RETRY_ATTEMPTS", "3"))
    MAIL_RETRY_DELAY_SECONDS: float = float(os.getenv("EMAIL_RETRY_DELAY_SECONDS", "0.5"))

@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()
