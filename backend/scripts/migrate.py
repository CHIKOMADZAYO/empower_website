#!/usr/bin/env python3
"""Run database migrations via Alembic (thin wrapper for automation + docs)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def migrate() -> None:
    """Upgrade the database to head using the repo-root alembic.ini."""
    root = Path(__file__).resolve().parents[2]
    backend = root / "backend"
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "-c", str(root / "alembic.ini"), "upgrade", "head"],
        cwd=backend,
    )
    if result.returncode != 0:
        raise SystemExit(result.returncode)
    print("Database migration completed")


if __name__ == "__main__":
    migrate()
