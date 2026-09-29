"""`deploy` — validate, build image, compose up, health-check (rollback hint)."""

from __future__ import annotations

import argparse

from automation.infrastructure.context import AppContext, AutomationError
from automation.services import docker_service, ops_service
from automation.services.env_service import has_errors, validate_environment

name = "deploy"
help = "Deploy: validate -> build -> up -> health check."


def register(sub: argparse._SubParsersAction) -> argparse.ArgumentParser:
    p = sub.add_parser(name, help=help, description=help)
    p.add_argument("--env", default="staging", choices=["staging", "production"])
    p.add_argument("--health-url", default="http://localhost:8000/api/v1/health")
    p.add_argument("--skip-build", action="store_true")
    return p


def run(args: argparse.Namespace, ctx: AppContext) -> int:
    issues = validate_environment(ctx, strict_prod=(args.env == "production"))
    for i in issues:
        (ctx.log.error if i.level == "error" else ctx.log.warning)("%s: %s", i.variable, i.message)
    if has_errors(issues):
        raise AutomationError(f"Deploy to {args.env} blocked by env errors.")
    if not args.skip_build:
        docker_service.docker_build(ctx)
    docker_service.compose(ctx, "up")
    try:
        ops_service.health_check(ctx, args.health_url)
    except AutomationError:
        ctx.log.error(
            "Deploy unhealthy — rollback: `docker compose down` then redeploy previous image."
        )
        raise
    ctx.log.info("Deploy to %s succeeded ✔", args.env)
    return 0
