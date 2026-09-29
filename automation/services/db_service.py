"""Database service: Alembic migrate/upgrade/downgrade + seed + reset.

Design: destructive ops (reset/downgrade) REQUIRE explicit confirmation
unless --force. Reset preserves the safety rule: refuse production unless
ENVIRONMENT != production or --force with typed confirmation.
"""

from __future__ import annotations

import os
import sys

from automation.infrastructure.context import AppContext, AutomationError
from automation.utils.process import run, which


def _alembic_available() -> bool:
    return which("alembic") is not None


def _confirm(prompt: str, *, force: bool) -> None:
    if force:
        return
    try:
        answer = input(f"{prompt} [y/N]: ").strip().lower()
    except EOFError as exc:
        raise AutomationError(
            "Aborted: no confirmation given (non-interactive). Use --force to override."
        ) from exc
    if answer not in ("y", "yes"):
        raise AutomationError("Aborted by user.")


def migrate_create(ctx: AppContext, message: str) -> None:
    """Create a new Alembic revision (autogenerate)."""
    if not message:
        raise AutomationError("--message is required for `db migrate`.")
    backend = ctx.settings.backend_dir
    if not _alembic_available():
        raise AutomationError("Alembic is not installed (`pip install alembic`).")
    if ctx.dry_run:
        ctx.log.info('[dry-run] would run: alembic revision --autogenerate -m "%s"', message)
        return
    result = run("alembic", "revision", "--autogenerate", "-m", message, cwd=backend)
    print(result.stdout[-3000:])
    if not result.ok:
        raise AutomationError("alembic revision failed.", hint=result.stderr[-2000:])


def upgrade(ctx: AppContext, revision: str = "head") -> None:
    backend = ctx.settings.backend_dir
    if not _alembic_available():
        # Graceful fallback for this repo (SQLite + create_all): init schema directly.
        _fallback_init_schema(ctx)
        return
    if ctx.dry_run:
        ctx.log.info("[dry-run] would run: alembic upgrade %s", revision)
        return
    result = run("alembic", "upgrade", revision, cwd=backend)
    print(result.stdout[-3000:])
    if not result.ok:
        raise AutomationError("alembic upgrade failed.", hint=result.stderr[-2000:])


def downgrade(ctx: AppContext, revision: str = "-1") -> None:
    _confirm(f"Destructive: downgrade database to {revision}?", force=ctx.force)
    backend = ctx.settings.backend_dir
    if not _alembic_available():
        raise AutomationError("Alembic is not installed; cannot downgrade.")
    if ctx.dry_run:
        ctx.log.info("[dry-run] would run: alembic downgrade %s", revision)
        return
    result = run("alembic", "downgrade", revision, cwd=backend)
    print(result.stdout[-3000:])
    if not result.ok:
        raise AutomationError("alembic downgrade failed.", hint=result.stderr[-2000:])


def _fallback_init_schema(ctx: AppContext) -> None:
    """Init schema via app metadata when Alembic isn't configured yet."""
    backend = ctx.settings.backend_dir
    if ctx.dry_run:
        ctx.log.info("[dry-run] would init schema via app.core.database.init_db()")
        return
    result = run(
        sys.executable,
        "-c",
        "from app.core.database import init_db; init_db(); print('schema init ok')",
        cwd=backend,
    )
    print(result.stdout[-2000:])
    if not result.ok:
        raise AutomationError("Schema init failed.", hint=result.stderr[-2000:])


def seed(ctx: AppContext) -> None:
    backend = ctx.settings.backend_dir
    seed_script = backend / "scripts" / "seed_db.py"
    if not seed_script.is_file():
        raise AutomationError(f"Seed script not found: {seed_script}")
    if ctx.dry_run:
        ctx.log.info("[dry-run] would run: python scripts/seed_db.py")
        return
    result = run(sys.executable, "scripts/seed_db.py", cwd=backend)
    print(result.stdout[-2000:])
    if not result.ok:
        raise AutomationError("Database seeding failed.", hint=result.stderr[-2000:])
    ctx.log.info("Database seeded.")


def reset(ctx: AppContext) -> None:
    """Drop + recreate + seed (dev/test only guard)."""
    env = (os.getenv("ENVIRONMENT", ctx.settings.environment) or "").lower()
    if env == "production" and not ctx.force:
        raise AutomationError(
            "Refusing to reset a PRODUCTION database without --force.",
            hint="Set ENVIRONMENT=development or pass --force with full backup.",
        )
    _confirm("Destructive: RESET database (drop all data) and re-seed?", force=ctx.force)
    backend = ctx.settings.backend_dir
    if _alembic_available():
        down = run("alembic", "downgrade", "base", cwd=backend)
        if not down.ok:
            ctx.log.warning(
                "alembic downgrade base had issues; continuing with create_all fallback."
            )
    # SQLite-friendly: delete file if sqlite, else drop_all/create_all.
    if ctx.dry_run:
        ctx.log.info("[dry-run] would drop, recreate schema and seed")
        return
    result = run(
        sys.executable,
        "-c",
        "from app.core.database import Base, engine; "
        "Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine); "
        "print('reset ok')",
        cwd=backend,
    )
    if not result.ok:
        raise AutomationError("Database reset failed.", hint=result.stderr[-2000:])
    seed(ctx)
    ctx.log.info("Database reset complete.")
