"""`db` command group: migrate / upgrade / downgrade / seed / reset."""

from __future__ import annotations

import argparse

from automation.infrastructure.context import AppContext
from automation.services import db_service

name = "db"
help = "Database operations (Alembic migrations, seeding, reset)."


def register(sub: argparse._SubParsersAction) -> argparse.ArgumentParser:
    p = sub.add_parser(name, help=help, description=help)
    db_sub = p.add_subparsers(dest="db_action", required=True, metavar="ACTION")

    m = db_sub.add_parser("migrate", help="Create a new Alembic revision (autogenerate).")
    m.add_argument(
        "-m", "--message", required=True, help="Revision message, e.g. -m 'add project index'."
    )

    u = db_sub.add_parser("upgrade", help="Upgrade to a revision (default: head).")
    u.add_argument("revision", nargs="?", default="head", help="Target revision (default: head).")

    d = db_sub.add_parser("downgrade", help="Destructive: downgrade one step (default: -1).")
    d.add_argument("revision", nargs="?", default="-1", help="Target revision (default: -1).")

    db_sub.add_parser("seed", help="Seed database with demo data (idempotent).")
    db_sub.add_parser("reset", help="Destructive: drop + recreate + seed (dev/test).")
    return p


def run(args: argparse.Namespace, ctx: AppContext) -> int:
    action = args.db_action
    if action == "migrate":
        db_service.migrate_create(ctx, args.message)
    elif action == "upgrade":
        db_service.upgrade(ctx, args.revision)
    elif action == "downgrade":
        db_service.downgrade(ctx, args.revision)
    elif action == "seed":
        db_service.seed(ctx)
    elif action == "reset":
        db_service.reset(ctx)
    return 0
