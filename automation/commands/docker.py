"""`docker` group: build / up / down / restart / logs / ps / migrate."""

from __future__ import annotations

import argparse

from automation.infrastructure.context import AppContext
from automation.services import docker_service

name = "docker"
help = "Docker & Compose management (build, up/down, logs, migrate)."


def register(sub: argparse._SubParsersAction) -> argparse.ArgumentParser:
    p = sub.add_parser(name, help=help, description=help)
    d = p.add_subparsers(dest="docker_action", required=True, metavar="ACTION")
    b = d.add_parser("build", help="Build images (docker compose build).")
    b.add_argument("--service", default=None, help="Only build this service.")
    for action in ("up", "down", "restart"):
        s = d.add_parser(action, help=f"Compose {action}.")
        s.add_argument("--service", default=None, help="Only affect this service.")
    lg = d.add_parser("logs", help="Show container logs.")
    lg.add_argument("--service", default=None)
    lg.add_argument("-f", "--follow", action="store_true")
    d.add_parser("ps", help="List containers.")
    mg = d.add_parser("migrate", help="Run `alembic upgrade head` inside backend container.")
    mg.add_argument("--service", default="backend")
    return p


def run(args: argparse.Namespace, ctx: AppContext) -> int:
    action = args.docker_action
    if action == "build":
        docker_service.docker_build(ctx, target=args.service)
    elif action == "migrate":
        docker_service.compose(ctx, "migrate", service=args.service)
    elif action == "logs":
        docker_service.compose(ctx, "logs", service=args.service, follow=args.follow)
    elif action in ("up", "down", "restart", "ps"):
        docker_service.compose(ctx, action, service=getattr(args, "service", None))
    return 0
