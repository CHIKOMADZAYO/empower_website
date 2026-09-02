"""FastAPI application factory."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import v1_router
from app.core.config import get_settings
from app.core.database import init_db


settings = get_settings()


def seed_database() -> None:
    """Seed database with local demo data when the database is empty."""
    from sqlalchemy.orm import Session
    from sqlalchemy import select

    from app.core.database import SessionLocal
    from app.core.security import hash_password
    from app.models.contact import ContactMessage
    from app.models.project import Project
    from app.models.story import Story
    from app.models.user import User
    from data.moct_data import (
        MOCK_CONTACT_MESSAGES,
        MOCK_PROJECTS,
        MOCK_STORIES,
        MOCK_USERS,
    )

    with Session(SessionLocal.kw["bind"]) as db:
        if db.scalar(select(User.id).limit(1)) is None:
            db.add_all([
                User(
                    username=user["username"],
                    email=user["email"],
                    hashed_password=hash_password(user["password"]),
                    role=user["role"],
                )
                for user in MOCK_USERS
            ])

        if db.scalar(select(Project.id).limit(1)) is None:
            db.add_all([
                Project(
                    name=project["name"],
                    category=project["category"],
                    summary=project["summary"],
                    description=project["description"],
                )
                for project in MOCK_PROJECTS
            ])

        if db.scalar(select(Story.id).limit(1)) is None:
            db.add_all([
                Story(
                    title=story["title"],
                    category=story["category"],
                    excerpt=story["excerpt"],
                    year=story["year"],
                )
                for story in MOCK_STORIES
            ])

        if db.scalar(select(ContactMessage.id).limit(1)) is None:
            db.add_all([
                ContactMessage(
                    name=message["name"],
                    email=message["email"],
                    message=message["message"],
                )
                for message in MOCK_CONTACT_MESSAGES
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
