"""Database tests: schema init + seed idempotency."""

import pytest

from app.core.database import Base, SessionLocal, engine
from app.models.contact import ContactMessage
from app.models.project import Project
from app.models.story import Story
from app.models.user import User

pytestmark = pytest.mark.integration


def test_tables_exist_after_create_all() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        assert db.query(User).all() == []
        assert db.query(Project).all() == []
        assert db.query(Story).all() == []
        assert db.query(ContactMessage).all() == []


def test_seed_database_is_idempotent() -> None:
    from app.main import seed_database

    seed_database()
    with SessionLocal() as db:
        users_first = db.query(User).count()
        assert users_first >= 1
    seed_database()
    with SessionLocal() as db:
        assert db.query(User).count() == users_first
