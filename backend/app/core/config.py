"""Application configuration and environment variables."""

import os
from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.engine import make_url

_backend_dir = Path(__file__).resolve().parents[2]
_project_root = _backend_dir.parent

for env_path in (_project_root / ".env", _backend_dir / ".env"):
    if env_path.exists():
        load_dotenv(env_path, override=env_path == _backend_dir / ".env")


class Settings:
    """Application settings from environment variables."""

    # Database
    DATABASE_URL: str = os.getenv(
        "EMPOWER_TEST_DATABASE_URL",
        os.getenv("DATABASE_URL", f"sqlite:///{_backend_dir / 'empower.db'}"),
    )

    def __init__(self) -> None:
        # SQLite paths are relative to the process working directory, which varies by
        # how the app is started. Always anchor them to the backend directory so a
        # restart points at the same database file.
        url = make_url(self.DATABASE_URL)
        if url.get_backend_name() == "sqlite" and url.database:
            database = Path(url.database)
            if not database.is_absolute():
                if database.parts and database.parts[0] == "backend":
                    absolute_database = (_backend_dir.parent / database).resolve()
                else:
                    absolute_database = (_backend_dir / database).resolve()
                self.DATABASE_URL = url.set(database=str(absolute_database)).render_as_string(
                    hide_password=False
                )

    # Security Settings
    SECRET_KEY: str = os.getenv("EMPOWER_SECRET_KEY", os.getenv("SECRET_KEY", ""))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # App Settings
    APP_NAME: str = "Empower API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "API for Empower's community-led programs and support network."
    ADMIN_BOOTSTRAP_TOKEN: str = os.getenv(
        "ADMIN_BOOTSTRAP_TOKEN", os.getenv("FIRST_ADMIN_BOOTSTRAP_TOKEN", "")
    )
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
