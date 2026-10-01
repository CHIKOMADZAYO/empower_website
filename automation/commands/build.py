"""`build` — gated pipeline. Stops at first critical failure (non-zero exit)."""

from __future__ import annotations

import argparse
import sys
import time
from collections.abc import Callable

from automation.infrastructure.context import AppContext, AutomationError
from automation.services import docker_service
from automation.services.quality_service import run_format, run_lint, run_typecheck
from automation.services.security_service import run_security
from automation.services.test_service import run_pytest
from automation.utils.output import step as step_fmt

name = "build"
help = (
    "Full pipeline: format -> lint -> typecheck -> unit -> "
    "integration -> security -> package -> docker."
)


def register(sub: argparse._SubParsersAction) -> argparse.ArgumentParser:
    p = sub.add_parser(name, help=help, description=help)
    p.add_argument("--skip-docker", action="store_true")
    p.add_argument("--skip-integration", action="store_true")
    return p


def _package(ctx: AppContext) -> None:
    from automation.utils.process import run as _run

    root = ctx.settings.project_root
    if ctx.dry_run:
        ctx.log.info("[dry-run] would build package into dist/")
        return
    if not (root / "pyproject.toml").is_file():
        raise AutomationError("Cannot build package: pyproject.toml was not found.")
    res = _run(sys.executable, "-m", "build", "--outdir", "dist", cwd=root)
    if not res.ok:
        raise AutomationError(
            "Python package build failed.", hint=(res.stdout + res.stderr)[-2000:]
        )
    ctx.log.info("Package built into dist/.")


def run(args: argparse.Namespace, ctx: AppContext) -> int:
    steps: list[tuple[str, Callable[[], None]]] = [
        ("Format check", lambda: run_format(ctx, check=True)),
        ("Lint", lambda: run_lint(ctx)),
        ("Typecheck", lambda: run_typecheck(ctx)),
        ("Unit tests", lambda: run_pytest(ctx, scope="unit")),
    ]
    if not args.skip_integration:
        steps.append(("Integration tests", lambda: run_pytest(ctx, scope="integration")))
    steps.append(("Security checks", lambda: run_security(ctx, strict=False)))
    total = len(steps) + 1 + (0 if args.skip_docker else 1)
    idx = 0
    for label, fn in steps:
        idx += 1
        print(step_fmt(idx, total, str(label)))
        t0 = time.monotonic()
        fn()
        ctx.log.info("%s done in %.1fs", label, time.monotonic() - t0)
    idx += 1
    print(step_fmt(idx, total, "Package"))
    _package(ctx)
    if not args.skip_docker:
        idx += 1
        print(step_fmt(idx, total, "Docker build"))
        try:
            docker_service.docker_build(ctx)
        except AutomationError:
            raise
    ctx.log.info("Build pipeline PASSED ✔")
    return 0
