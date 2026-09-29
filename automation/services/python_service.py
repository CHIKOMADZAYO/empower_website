"""Python/dependency management service (setup + install paths)."""

from __future__ import annotations

import os
import shutil
import sys
import venv
from pathlib import Path

from automation.infrastructure.context import AppContext, AutomationError
from automation.utils.process import run, which


def python_version_ok(min_major: int = 3, min_minor: int = 12) -> tuple[bool, str]:
    v = sys.version_info
    return ((v.major, v.minor) >= (min_major, min_minor), f"{v.major}.{v.minor}.{v.micro}")


def ensure_venv(ctx: AppContext, venv_dir: Path | None = None) -> Path:
    """Idempotently create venv. Returns venv python path."""
    target = venv_dir or (ctx.settings.backend_dir / ".venv")
    if ctx.dry_run:
        ctx.log.info("[dry-run] would ensure venv at %s", target)
        return target / "bin" / "python"
    if (
        not (target / "bin" / "python").exists()
        and not (target / "Scripts" / "python.exe").exists()
    ):
        ctx.log.info("Creating virtual environment at %s ...", target)
        venv.create(target, with_pip=True)
    else:
        ctx.log.info("Virtual environment already exists at %s", target)
    cand = target / "bin" / "python"
    if not cand.exists():
        cand = target / "Scripts" / "python.exe"
    return cand


def pip_install(ctx: AppContext, requirements: Path, python_bin: str | None = None) -> None:
    """Install requirements with the venv (or current) python."""
    if not requirements.is_file():
        raise AutomationError(f"Requirements file not found: {requirements}")
    py = python_bin or sys.executable
    if ctx.dry_run:
        ctx.log.info("[dry-run] would run: %s -m pip install -r %s", py, requirements)
        return
    ctx.log.info("Installing dependencies from %s ...", requirements)
    result = run(py, "-m", "pip", "install", "--upgrade", "pip", cwd=ctx.settings.project_root)
    if not result.ok:
        raise AutomationError("Failed to upgrade pip.", hint=result.stderr[-1000:])
    result = run(py, "-m", "pip", "install", "-r", str(requirements), cwd=ctx.settings.project_root)
    if not result.ok:
        raise AutomationError(
            f"pip install failed for {requirements.name}.", hint=result.stderr[-2000:]
        )
    ctx.log.info("Dependencies installed.")


def ensure_env_file(ctx: AppContext) -> Path:
    """Idempotently create .env from .env.example (never overwrites)."""
    settings = ctx.settings
    candidates = [settings.backend_env_example, settings.env_example]
    template = next((c for c in candidates if c.is_file()), None)
    # Backend .env lives next to backend/.env.example
    dest = settings.backend_dir / ".env"
    if dest.is_file():
        ctx.log.info(".env already exists at %s (leaving untouched)", dest)
        return dest
    if template is None:
        raise AutomationError("No .env.example template found; cannot create .env.")
    if ctx.dry_run:
        ctx.log.info("[dry-run] would copy %s -> %s", template, dest)
        return dest
    shutil.copy(template, dest)
    ctx.log.warning("Created %s from %s — review secrets before use.", dest, template)
    return dest


def tool_available(name: str) -> str | None:
    return which(name) or os.getenv(name.upper().replace("-", "_"))
