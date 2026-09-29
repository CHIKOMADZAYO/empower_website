"""`security` command: deps, secrets, env, bandit, Dockerfile sanity."""

from __future__ import annotations

import argparse

from automation.infrastructure.context import AppContext
from automation.services.security_service import run_security

name = "security"
help = "Run security checks (deps, secrets, env, bandit, Dockerfile)."


def register(sub: argparse._SubParsersAction) -> argparse.ArgumentParser:
    p = sub.add_parser(name, help=help, description=help)
    p.add_argument("--strict", action="store_true", help="Strict/prod-mode env validation.")
    return p


def run(args: argparse.Namespace, ctx: AppContext) -> int:
    run_security(ctx, strict=args.strict)
    return 0
