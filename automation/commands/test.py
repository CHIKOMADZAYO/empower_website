"""`test` command with --unit/--integration/--api/--coverage selectors."""

from __future__ import annotations

import argparse

from automation.infrastructure.context import AppContext
from automation.services.test_service import run_pytest

name = "test"
help = "Run pytest suites (all/unit/integration/api, optional coverage)."


def register(sub: argparse._SubParsersAction) -> argparse.ArgumentParser:
    p = sub.add_parser(name, help=help, description=help)
    g = p.add_mutually_exclusive_group()
    g.add_argument("--unit", action="store_true", help="Unit tests only (-m 'not integration').")
    g.add_argument(
        "--integration", action="store_true", help="Integration tests only (-m integration)."
    )
    g.add_argument("--api", action="store_true", help="API tests only (-k endpoint/api/auth/...).")
    p.add_argument("--coverage", action="store_true", help="Run with coverage report.")
    p.add_argument(
        "extra", nargs=argparse.REMAINDER, help="Extra args passed to pytest after '--'."
    )
    return p


def run(args: argparse.Namespace, ctx: AppContext) -> int:
    scope = "all"
    if args.unit:
        scope = "unit"
    elif args.integration:
        scope = "integration"
    elif args.api:
        scope = "api"
    extra = tuple(a for a in (args.extra or []) if a != "--")
    run_pytest(ctx, scope=scope, coverage=args.coverage, extra_args=extra)
    return 0
