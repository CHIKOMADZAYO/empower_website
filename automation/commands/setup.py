"""`setup` — idempotent dev environment bootstrap."""

from __future__ import annotations

import argparse
import socket
import sys

from automation.config.settings import REQUIRED_SERVICES
from automation.infrastructure.context import AppContext
from automation.services import db_service, env_service, python_service
from automation.services.test_service import run_pytest

name = "setup"
help = "Bootstrap dev environment (idempotent): venv, deps, .env, validate, migrate, smoke tests."


def register(sub: argparse._SubParsersAction) -> argparse.ArgumentParser:
    p = sub.add_parser(name, help=help, description=help)
    p.add_argument("--no-venv", action="store_true", help="Skip virtualenv creation.")
    p.add_argument("--no-install", action="store_true", help="Skip dependency installation.")
    p.add_argument("--no-migrate", action="store_true", help="Skip DB schema init/migrations.")
    p.add_argument("--no-test", action="store_true", help="Skip smoke tests.")
    p.add_argument(
        "--check-services",
        action="store_true",
        help="Check external services (Postgres/Redis) reachability.",
    )
    p.add_argument("--seed", action="store_true", help="Seed database after migrate.")
    return p


def _check_services(ctx: AppContext) -> None:
    for host, port, label in REQUIRED_SERVICES:
        try:
            with socket.create_connection((host, port), timeout=2):
                ctx.log.info("%s reachable at %s:%d", label, host, port)
        except OSError:
            optional = "optional" in label.lower()
            (ctx.log.warning if optional else ctx.log.error)(
                "%s NOT reachable at %s:%d%s",
                label,
                host,
                port,
                " (ok to ignore for SQLite dev)" if optional else "",
            )


def run(args: argparse.Namespace, ctx: AppContext) -> int:
    log = ctx.log
    log.info("Setup: checking Python version ...")
    ok_ver, ver = python_service.python_version_ok()
    log.info("Python %s %s", ver, "(OK)" if ok_ver else "(WARNING: want 3.12+)")

    python_bin = sys.executable
    if not args.no_venv:
        python_bin = str(python_service.ensure_venv(ctx))
    if not args.no_install:
        req = ctx.settings.backend_dir / "requirements.txt"
        if req.is_file():
            python_service.pip_install(
                ctx, req, python_bin=python_bin if not args.no_venv else None
            )
        else:
            log.warning("No requirements file at %s — skipping install.", req)
    try:
        python_service.ensure_env_file(ctx)
    except Exception as exc:  # keep setup going; validation will report
        log.warning("Could not create .env: %s", exc)

    issues = env_service.validate_environment(ctx)
    for i in issues:
        (log.error if i.level == "error" else log.warning)("%s: %s", i.variable, i.message)
    if env_service.has_errors(issues):
        log.error("Setup halted: fix environment errors above.")
        return 1

    if args.check_services:
        _check_services(ctx)
    if not args.no_migrate:
        try:
            db_service.upgrade(ctx)
        except Exception as exc:
            log.error("Migration step failed: %s", exc)
            return 1
    if args.seed:
        try:
            db_service.seed(ctx)
        except Exception as exc:
            log.error("Seeding failed: %s", exc)
            return 1
    if not args.no_test:
        try:
            run_pytest(ctx, scope="all")
        except Exception as exc:
            log.warning("Smoke tests reported issues: %s", exc)
    log.info("Setup complete ✔")
    return 0
