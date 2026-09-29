"""Docker / Compose service."""

from __future__ import annotations

from automation.infrastructure.context import AppContext, AutomationError
from automation.utils.process import run, which


def _compose(ctx: AppContext) -> list[str]:
    if which("docker") is None:
        raise AutomationError("Docker is not installed or not on PATH.")
    # Prefer `docker compose` v2; fall back to `docker-compose` v1.
    probe = run("docker", "compose", "version", cwd=ctx.settings.project_root)
    if probe.ok:
        return ["docker", "compose"]
    if which("docker-compose"):
        return ["docker-compose"]
    raise AutomationError("Docker Compose not found (`docker compose` or `docker-compose`).")


def _compose_file_args(ctx: AppContext) -> list[str]:
    compose = ctx.settings.compose_file
    if compose.is_file():
        return ["-f", str(compose)]
    return []


def docker_build(ctx: AppContext, *, target: str | None = None) -> None:
    base = _compose(ctx) + _compose_file_args(ctx) + ["build"]
    if target:
        base.append(target)
    if ctx.dry_run:
        ctx.log.info("[dry-run] would run: %s", " ".join(base))
        return
    result = run(*base, cwd=ctx.settings.project_root, timeout=1200)
    print(result.stdout[-3000:])
    if not result.ok:
        raise AutomationError("Docker build failed.", hint=result.stderr[-2000:])


def compose(
    ctx: AppContext, action: str, *, service: str | None = None, follow: bool = False
) -> None:
    """up | down | restart | logs | ps | migrate."""
    base = _compose(ctx) + _compose_file_args(ctx)
    if action == "up":
        cmd = base + ["up", "-d", "--build"] + ([service] if service else [])
    elif action == "down":
        cmd = base + ["down"] + ([service] if service else [])
    elif action == "restart":
        cmd = base + ["restart"] + ([service] if service else [])
    elif action == "ps":
        cmd = base + ["ps"]
    elif action == "logs":
        cmd = (
            base
            + ["logs", "--tail=200"]
            + (["-f"] if follow else [])
            + ([service] if service else [])
        )
    elif action == "migrate":
        # Run migrations inside the backend container.
        svc = service or "backend"
        cmd = base + ["exec", svc, "alembic", "upgrade", "head"]
    else:
        raise AutomationError(f"Unknown compose action: {action}")
    if ctx.dry_run:
        ctx.log.info("[dry-run] would run: %s", " ".join(cmd))
        return
    result = run(*cmd, cwd=ctx.settings.project_root, timeout=900)
    print((result.stdout or result.stderr)[-3000:])
    if not result.ok:
        raise AutomationError(f"docker {action} failed.", hint=result.stderr[-2000:])
