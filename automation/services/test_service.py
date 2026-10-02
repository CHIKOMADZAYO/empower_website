"""Test service: unit / integration / api / coverage via pytest markers."""

from __future__ import annotations

import sys
from pathlib import Path

from automation.infrastructure.context import AppContext, AutomationError
from automation.utils.process import run

# Convention (documented in README + pyproject):
# - backend/tests/test_auth.py, test_db.py -> unit (default)
# - backend/tests/test_endpoints.py         -> integration (@pytest.mark.integration)
# - automation/tests/                       -> automation CLI self-tests (fast unit)


def _run_suite(
    ctx: AppContext,
    *,
    cwd: Path | str,
    args: list[str],
    label: str,
    env: dict[str, str] | None = None,
) -> None:
    cmd = [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", *args]
    if ctx.dry_run:
        ctx.log.info("[dry-run] would run in %s: %s", cwd, " ".join(cmd))
        return
    ctx.log.info("Running %s ...", label)
    result = run(*cmd, cwd=cwd, timeout=900, env=env)
    print(result.stdout[-4000:])
    if not result.ok:
        raise AutomationError(
            f"{label} failed.", hint=result.stderr[-2000:] or result.stdout[-2000:]
        )
    ctx.log.info("%s passed.", label)


def run_pytest(
    ctx: AppContext,
    *,
    scope: str = "all",  # all | unit | integration | api
    coverage: bool = False,
    extra_args: tuple[str, ...] = (),
) -> None:
    backend = ctx.settings.backend_dir
    args: list[str] = []
    if scope == "unit":
        args += ["-m", "not integration"]
    elif scope == "integration":
        args += ["-m", "integration"]
    elif scope == "api":
        args += ["-k", "endpoint or api or auth or contact or project or story"]
    if coverage:
        args += ["--cov=app", "--cov-report=term-missing", "--cov-report=xml"]
    args += list(extra_args)
    # Isolate pytest runs from the developer's real DB: point SQLite at a
    # throwaway file unless the caller explicitly set EMPOWER_TEST_DATABASE_URL.
    # (Prevents "database is locked" when the dev server owns empower.db.)
    test_env: dict[str, str] | None = None
    backend_url = ctx.settings.database_url or ""
    if not backend_url or "sqlite" in backend_url:
        import os
        import tempfile

        if not os.getenv("EMPOWER_TEST_DATABASE_URL"):
            tmp = tempfile.NamedTemporaryFile(prefix="empower-test-", suffix=".db", delete=False)
            tmp.close()
            test_env = {"EMPOWER_TEST_DATABASE_URL": f"sqlite:///{tmp.name}"}
    _run_suite(ctx, cwd=backend, args=args, label=f"backend {scope} tests", env=test_env)
    if scope in ("all", "unit"):
        # Fast automation-CLI self tests; always part of unit/all runs.
        _run_suite(
            ctx,
            cwd=ctx.settings.project_root,
            args=["automation/tests", "-q"],
            label="automation tests",
        )
