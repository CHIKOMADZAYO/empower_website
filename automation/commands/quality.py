"""format / lint / typecheck commands (thin wrappers over quality_service)."""

from __future__ import annotations

import argparse

from automation.infrastructure.context import AppContext
from automation.services import quality_service


def _std(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--check", action="store_true", help="Check only; do not modify files (CI mode)."
    )


def _register_format(sub: argparse._SubParsersAction) -> None:
    p = sub.add_parser(
        "format", help="Format code with Ruff.", description="Run `ruff format` on the backend."
    )
    _std(p)


def _run_format(args: argparse.Namespace, ctx: AppContext) -> int:
    quality_service.run_format(ctx, check=args.check)
    return 0


def _register_lint(sub: argparse._SubParsersAction) -> None:
    sub.add_parser(
        "lint", help="Lint code with Ruff.", description="Run `ruff check` on the backend."
    )


def _run_lint(args: argparse.Namespace, ctx: AppContext) -> int:
    quality_service.run_lint(ctx)
    return 0


def _register_typecheck(sub: argparse._SubParsersAction) -> None:
    sub.add_parser(
        "typecheck", help="Type-check with mypy.", description="Run `mypy app` in the backend."
    )


def _run_typecheck(args: argparse.Namespace, ctx: AppContext) -> int:
    quality_service.run_typecheck(ctx)
    return 0


# Module-level command descriptors consumed by the CLI registry.
COMMANDS = [
    ("format", "Format code with Ruff.", _register_format, _run_format),
    ("lint", "Lint code with Ruff.", _register_lint, _run_lint),
    ("typecheck", "Type-check with mypy.", _register_typecheck, _run_typecheck),
]
