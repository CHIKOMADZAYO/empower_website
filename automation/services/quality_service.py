"""Quality service: ruff format/lint + mypy. Single place for quality gates."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

from automation.infrastructure.context import AppContext, AutomationError
from automation.utils.process import run


def _resolve(cmd: str) -> list[str]:
    """Prefer a venv binary, then PATH, then `python -m <cmd>` fallback."""
    if shutil.which(cmd):
        return [cmd]
    for venv_bin in (Path(sys.executable).parent / cmd,):
        if venv_bin.exists():
            return [str(venv_bin)]
    return [sys.executable, "-m", cmd]


def _run_tool(ctx: AppContext, *cmd: str, cwd=None, label: str) -> None:
    if ctx.dry_run:
        ctx.log.info("[dry-run] would run: %s", " ".join(cmd))
        return
    result = run(*cmd, cwd=cwd or ctx.settings.backend_dir)
    if result.stdout.strip():
        ctx.log.debug("%s stdout:\n%s", label, result.stdout[-3000:])
    if not result.ok:
        raise AutomationError(f"{label} failed.", hint=(result.stdout + result.stderr)[-2500:])


def _targets(ctx: AppContext) -> list[str]:
    """Absolute lint/format targets: backend code + automation package."""
    b = ctx.settings.backend_dir
    return [
        str(b / "app"),
        str(b / "tests"),
        str(b / "scripts"),
        str(ctx.settings.project_root / "automation"),
    ]


def run_format(ctx: AppContext, *, check: bool = False) -> None:
    """Ruff format (or check) over backend + automation (skips venvs)."""
    base = _resolve("ruff") + ["format", *_targets(ctx)]
    if check:
        base = _resolve("ruff") + ["format", "--check", *_targets(ctx)]
    try:
        _run_tool(ctx, *base, cwd=ctx.settings.backend_dir, label="ruff format")
    except AutomationError:
        raise
    except Exception as exc:
        raise AutomationError(
            "ruff is not installed. Run `setup` or `pip install ruff`.", hint=str(exc)
        ) from exc
    ctx.log.info("Formatting OK.")


def run_lint(ctx: AppContext) -> None:
    try:
        _run_tool(
            ctx,
            *_resolve("ruff"),
            "check",
            *_targets(ctx),
            cwd=ctx.settings.backend_dir,
            label="ruff lint",
        )
    except AutomationError:
        raise
    except Exception as exc:
        raise AutomationError(
            "ruff is not installed. Run `setup` or `pip install ruff`.", hint=str(exc)
        ) from exc
    ctx.log.info("Lint OK.")


def run_typecheck(ctx: AppContext) -> None:
    try:
        _run_tool(
            ctx,
            *_resolve("mypy"),
            "backend/app",
            cwd=ctx.settings.project_root,
            label="mypy typecheck",
        )
    except AutomationError:
        raise
    except Exception as exc:
        raise AutomationError(
            "mypy is not installed. Run `setup` or `pip install mypy`.", hint=str(exc)
        ) from exc
    ctx.log.info("Typecheck OK.")
