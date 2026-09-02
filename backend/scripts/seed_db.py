#!/usr/bin/env python3
"""Seed the database with sample data for local development."""

import sys
from pathlib import Path

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
        if db.query(User).first() is None:
            db.add_all(
                [
                    User(
                        username=item["username"],
                        email=item["email"],
                        hashed_password=hash_password(item["password"]),
                        role=item["role"],
                    )
                    for item in MOCK_USERS
                ]
            )

        if db.query(Project).first() is None:
            db.add_all(
                [
                    Project(
                        name=item["name"],
                        category=item["category"],
                        summary=item["summary"],
                        description=item["description"],
                    )
                    for item in MOCK_PROJECTS
                ]
            )

        if db.query(Story).first() is None:
            db.add_all(
                [
                    Story(
                        title=item["title"],
                        category=item["category"],
                        excerpt=item["excerpt"],
                        year=item["year"],
                    )
                    for item in MOCK_STORIES
                ]
            )

        if db.query(ContactMessage).first() is None:
            db.add_all(
                [
                    ContactMessage(
                        name=item["name"],
                        email=item["email"],
                        message=item["message"],
                    )
                    for item in MOCK_CONTACT_MESSAGES
                ]
            )

        db.commit()

    print("Database seeding completed")


if __name__ == '__main__':
    seed_database()
