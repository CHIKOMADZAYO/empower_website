#!/usr/bin/env python3
"""Seed the database with sample data for local development."""

import sys
from pathlib import Path

from sqlalchemy import select

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.models.contact import ContactMessage
from app.models.project import Project
from app.models.story import Story
from app.models.user import User
from data.moct_data import MOCK_CONTACT_MESSAGES, MOCK_PROJECTS, MOCK_STORIES, MOCK_USERS


def seed_database() -> None:
    """Create the tables and insert mock application data if empty."""
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        for item in MOCK_USERS:
            if db.scalar(select(User.id).where(User.username == item["username"])) is None:
                db.add(User(
                    username=item["username"],
                    email=item["email"],
                    hashed_password=hash_password(item["password"]),
                    role=item["role"],
                ))

        for item in MOCK_PROJECTS:
            if db.scalar(select(Project.id).where(Project.name == item["name"])) is None:
                db.add(Project(**item))

        for item in MOCK_STORIES:
            if db.scalar(select(Story.id).where(Story.title == item["title"])) is None:
                db.add(Story(**item))

        for item in MOCK_CONTACT_MESSAGES:
            if db.scalar(select(ContactMessage.id).where(
                ContactMessage.email == item["email"],
                ContactMessage.message == item["message"],
            )) is None:
                db.add(ContactMessage(**item))

        db.commit()

    print("Database seeding completed")


if __name__ == '__main__':
    seed_database()
