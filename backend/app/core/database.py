"""Database connection and session management."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()
is_sqlite = make_url(settings.DATABASE_URL).get_backend_name() == "sqlite"

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 30} if is_sqlite else {},
    pool_pre_ping=not is_sqlite,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


def get_db() -> Generator[Session, None, None]:
    """Dependency: get database session."""
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()


def init_db() -> None:
    """Initialize database - create all tables."""
    from app.models.contact import ContactMessage  # noqa: F401
    from app.models.project import Project  # noqa: F401
    from app.models.story import Story  # noqa: F401
    from app.models.user import User  # noqa: F401

    Base.metadata.create_all(bind=engine)
