"""FastAPI application factory."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import v1_router
from app.core.config import get_settings
from app.core.database import init_db


settings = get_settings()


def seed_database() -> None:
    """Seed database with initial data."""
    from sqlalchemy.orm import Session
    from sqlalchemy import select

    from app.core.database import SessionLocal
    from app.models.project import Project
    from app.models.story import Story
    from app.models.user import User
    from app.core.security import hash_password

    with Session(SessionLocal.kw["bind"]) as db:
        if db.scalar(select(User.id).limit(1)) is None:
            db.add_all([
                User(
                    username="alice",
                    email="alice@empower.org",
                    hashed_password=hash_password("admin-pass-123"),
                    role="admin"
                ),
                User(
                    username="william",
                    email="william@empower.org",
                    hashed_password=hash_password("editor-pass-123"),
                    role="editor"
                ),
                User(
                    username="Ben",
                    email="ben@empower.org",
                    hashed_password=hash_password("viewer-pass-123"),
                    role="viewer"
                ),
            ])

        if db.scalar(select(Project.id).limit(1)) is None:
            db.add_all([
                Project(
                    name="Learning",
                    category="Education",
                    summary="Open doors to opportunity.",
                    description="We support mentors, teachers, and young people with learning spaces, practical skills, and pathways into work.",
                ),
                Project(
                    name="Wellbeing",
                    category="Health",
                    summary="Care that meets people where they are.",
                    description="Local health champions connect families to trusted information, care, and one another.",
                ),
                Project(
                    name="Opportunity",
                    category="Livelihoods",
                    summary="Ideas with room to grow.",
                    description="We help community enterprises build resilient livelihoods through training, networks, and patient support.",
                ),
            ])

        if db.scalar(select(Story.id).limit(1)) is None:
            db.add_all([
                Story(
                    title="The library became our meeting place.",
                    category="Learning",
                    excerpt="A community reading room became a place for young people to study, meet, and see new possibilities.",
                    year=2025,
                ),
                Story(
                    title="We are growing something that is ours.",
                    category="Opportunity",
                    excerpt="A cooperative of local makers is building reliable incomes while keeping traditional knowledge alive.",
                    year=2024,
                ),
            ])

        db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Startup
    init_db()
    seed_database()
    yield
    # Shutdown (cleanup if needed)


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        lifespan=lifespan,
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
    )

    # Include routers
    app.include_router(v1_router)

    return app


# Create app instance for uvicorn
app = create_app()
