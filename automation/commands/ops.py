"""`health` and `check` (pre-commit) commands."""

from __future__ import annotations

import argparse

from automation.infrastructure.context import AppContext
from automation.services import ops_service
from automation.services.ops_service import git_checks
from automation.services.quality_service import run_format, run_lint, run_typecheck
from automation.services.test_service import run_pytest

COMMANDS = []


def _reg_health(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser(
        "health",
        help="GET a health endpoint and verify it.",
        description="GET a health endpoint and verify 200 + healthy payload.",
    )
    p.add_argument("--url", default="http://localhost:8000/api/v1/health")
    p.add_argument("--timeout", type=int, default=10)


def _run_health(args: argparse.Namespace, ctx: AppContext) -> int:
    ops_service.health_check(ctx, args.url, timeout_s=args.timeout)
    return 0


def _reg_check(sub: argparse._SubParsersAction) -> None:
    sub.add_parser(
        "check",
        help="Pre-commit validation (format+lint+types+unit).",
        description="Pre-commit validation: git checks, format check, lint, typecheck, unit tests.",
    )


def _run_check(args: argparse.Namespace, ctx: AppContext) -> int:
    git_checks(ctx)
    run_format(ctx, check=True)
    run_lint(ctx)
    run_typecheck(ctx)
    run_pytest(ctx, scope="unit")
    ctx.log.info("Pre-commit checks passed ✔")
    return 0


COMMANDS = [
    ("health", "GET a health endpoint and verify it.", _reg_health, _run_health),
    ("check", "Pre-commit validation (format+lint+types+unit).", _reg_check, _run_check),
]
