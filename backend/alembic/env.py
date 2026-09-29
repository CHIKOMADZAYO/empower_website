"""Alembic environment: autogenerate from SQLAlchemy metadata."""
from __future__ import annotations

import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# backend/ on sys.path so `app.*` imports work when run from repo root.
BACKEND = Path(__file__).resolve().parents[1]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from app.core.database import Base  # noqa: E402

import app.models  # noqa: E402,F401  (register all models for autogenerate)

target_metadata = Base.metadata


def get_url() -> str:
    return os.getenv(
        "DATABASE_URL",
        f"sqlite:///{BACKEND / 'empower.db'}",
    )


def run_migrations_offline() -> None:
    context.configure(url=get_url(), target_metadata=target_metadata, literal_binds=True,
                      dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    config.set_main_option("sqlalchemy.url", get_url())
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
