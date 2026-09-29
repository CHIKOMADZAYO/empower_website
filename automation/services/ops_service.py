"""Git / pre-commit validation + release helpers + health checks."""

from __future__ import annotations

import json
import re
import urllib.request
from pathlib import Path

from automation.infrastructure.context import AppContext, AutomationError
from automation.utils.process import run, which

_CONVENTIONAL = re.compile(r"^(feat|fix|docs|style|refactor|test|chore|ci|build|perf)(\(.+\))?: .+")


def git_checks(ctx: AppContext) -> None:
    """Validate branch status + last commit message convention (warning-only)."""
    if which("git") is None:
        raise AutomationError("git is not installed.")
    root = ctx.settings.project_root
    status = run("git", "status", "--porcelain", cwd=root)
    if status.ok and status.stdout.strip() and not ctx.dry_run:
        ctx.log.warning("Working tree has uncommitted changes.")
    msg = run("git", "log", "-1", "--pretty=%s", cwd=root)
    if msg.ok and msg.stdout.strip() and not _CONVENTIONAL.match(msg.stdout.strip()):
        ctx.log.warning(
            "Last commit message is not Conventional Commits style: %r", msg.stdout.strip()
        )
    else:
        ctx.log.info("Git checks OK.")


def health_check(ctx: AppContext, url: str, *, timeout_s: int = 10) -> dict:
    """GET <url> and expect 200 + status ok/healthy. Returns parsed payload."""
    if ctx.dry_run:
        ctx.log.info("[dry-run] would GET %s", url)
        return {"status": "dry-run"}
    ctx.log.info("Health check: GET %s", url)
    req = urllib.request.Request(url, headers={"User-Agent": "empower-automation/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            status = resp.status
    except Exception as exc:
        raise AutomationError(f"Health check failed for {url}: {exc}") from exc
    try:
        payload = json.loads(body) if body else {}
    except json.JSONDecodeError:
        payload = {"raw": body[:500]}
    if status != 200:
        raise AutomationError(
            f"Health check returned HTTP {status} for {url}.", hint=str(payload)[:500]
        )
    marker = str(payload.get("status", "")).lower() if isinstance(payload, dict) else ""
    if isinstance(payload, dict) and payload and marker not in ("ok", "healthy", "up"):
        raise AutomationError(f"Health endpoint unhealthy: {url}.", hint=str(payload)[:500])
    ctx.log.info("Health check passed (%s).", url)
    return payload if isinstance(payload, dict) else {"raw": payload}


def bump_version_file(pyproject: Path, bump: str) -> str:
    """Bump x.y.z version in pyproject.toml. Returns new version."""
    text = pyproject.read_text(encoding="utf-8")
    m = re.search(r'^version\s*=\s*"(\d+)\.(\d+)\.(\d+)"', text, re.M)
    if not m:
        raise AutomationError(f"No x.y.z version found in {pyproject}.")
    major, minor, patch = map(int, m.groups())
    if bump == "major":
        major, minor, patch = major + 1, 0, 0
    elif bump == "minor":
        minor, patch = minor + 1, 0
    else:
        patch += 1
    new = f"{major}.{minor}.{patch}"
    pyproject.write_text(
        text[: m.start(1) - 1] + f'"{new}"' + text[m.end(3) + 1 :],
        encoding="utf-8",
    )
    return new


def git_tag(ctx: AppContext, version: str) -> None:
    root = ctx.settings.project_root
    tag = f"v{version}"
    if ctx.dry_run:
        ctx.log.info("[dry-run] would run: git tag -a %s -m ... && git push --tags", tag)
        return
    res = run("git", "tag", "-a", tag, "-m", f"Release {tag}", cwd=root)
    if not res.ok and "already exists" not in res.stderr:
        raise AutomationError(f"git tag failed: {tag}", hint=res.stderr[-1000:])
    ctx.log.info("Tagged %s", tag)
