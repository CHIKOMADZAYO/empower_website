"""Database tests: schema init + seed idempotency."""

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.core.database import Base, SessionLocal, engine
from app.models.contact import ContactMessage
from app.models.project import Project
from app.models.story import Story
from app.models.user import User

pytestmark = pytest.mark.integration


def test_tables_exist_after_create_all() -> None:
    from app.core.config import _backend_dir

    assert engine.url.database != str((_backend_dir / "empower.db").resolve())
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        assert db.query(User).all() == []
        assert db.query(Project).all() == []
        assert db.query(Story).all() == []
        assert db.query(ContactMessage).all() == []


def test_unknown_user_roles_are_rejected_by_database() -> None:
    """The persisted role constraint prevents unsupported privilege labels."""
    with SessionLocal() as db:
        with pytest.raises(IntegrityError):
            db.execute(
                text(
                    "INSERT INTO users (username, email, hashed_password, role, is_active) "
                    "VALUES ('invalid-role', 'invalid-role@example.com', 'hash', 'owner', 1)"
                )
            )


def test_sqlite_relative_path_is_resolved_to_backend_db(monkeypatch: pytest.MonkeyPatch) -> None:
    """Relative SQLite paths should always land on the same backend database file."""
    import app.core.config as config_module

    monkeypatch.setattr(config_module.Settings, "DATABASE_URL", "sqlite:///./backend/empower.db")
    config_module.get_settings.cache_clear()
    settings = config_module.get_settings()

    expected = (config_module.Path(__file__).resolve().parents[1] / "empower.db").resolve()
    assert config_module.Path(settings.DATABASE_URL.replace("sqlite:///", "")).resolve() == expected

    config_module.get_settings.cache_clear()


def test_app_does_not_seed_mock_data_on_startup() -> None:
    import app.main as app_main

    assert not hasattr(app_main, "seed_database")
    with SessionLocal() as db:
        assert db.query(User).count() == 0
