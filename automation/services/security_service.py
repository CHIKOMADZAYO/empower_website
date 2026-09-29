"""Security service: secrets never printed; tools optional with clear skips.

Checks:
1. pip-audit (dependency vulns) — optional, warn-skip if missing.
2. Secret patterns scan over tracked source files (API keys, private keys).
3. Env validation in strict/prod mode.
4. Bandit static analysis — optional, warn-skip if missing.
5. Dockerfile lint-ish sanity (no hardcoded secrets / running as root note).
"""

from __future__ import annotations

import re
from pathlib import Path

from automation.infrastructure.context import AppContext, AutomationError
from automation.services.env_service import has_errors, validate_environment
from automation.utils.process import run, which

_SECRET_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("aws-key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("private-key", re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    (
        "generic-secret-assign",
        re.compile(r"(?i)\b(secret|passwd|api[_-]?key)\b\s*[:=]\s*['\"][^'\"]{8,}['\"]"),
    ),
    ("jwt-in-file", re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")),
)

_SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "node_modules",
    "dist",
    ".pytest_cache",
    "htmlcov",
}
_SKIP_SUFFIX = {".pyc", ".png", ".jpg", ".jpeg", ".ico", ".svg", ".lock"}


def scan_secrets(ctx: AppContext) -> list[str]:
    """Return list of findings (paths + rule). Never includes secret values."""
    import os

    root = ctx.settings.project_root
    findings: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS and not d.startswith(".git")]
        if "frontend" in Path(dirpath).parts:
            continue
        for fname in filenames:
            if Path(fname).suffix in _SKIP_SUFFIX or fname in {
                ".env",
                "empower.db",
                "coverage.xml",
            }:
                continue
            if fname.endswith((".map", ".js", ".min.js")):
                continue
            fpath = Path(dirpath) / fname
            try:
                if fpath.stat().st_size > 300_000:
                    continue
            except OSError:
                continue
            try:
                text = fpath.read_text(encoding="utf-8", errors="strict")
            except (UnicodeDecodeError, OSError, ValueError):
                continue
            if len(text) > 300_000:
                continue
            for rule, pattern in _SECRET_PATTERNS:
                if pattern.search(text):
                    findings.append(f"{fpath.relative_to(root)} [{rule}]")
                    break
            if len(findings) > 50:
                return findings
    return findings


def run_security(ctx: AppContext, *, strict: bool = False) -> None:
    ctx.log.info("Running security checks ...")
    failures: list[str] = []

    # 1) pip-audit (optional). Warn-only by default; --strict makes it blocking.
    if which("pip-audit"):
        if ctx.dry_run:
            ctx.log.info("[dry-run] would run: pip-audit")
        else:
            res = run("pip-audit", cwd=ctx.settings.backend_dir)
            print(res.stdout[-2500:])
            if not res.ok:
                msg = "pip-audit reported vulnerabilities."
                if strict:
                    failures.append(msg)
                else:
                    ctx.log.warning("%s (non-blocking; use --strict to fail)", msg)
    else:
        ctx.log.warning(
            "pip-audit not installed — skipping dependency audit (pip install pip-audit)."
        )

    # 2) secret scan (always)
    findings = [] if ctx.dry_run else scan_secrets(ctx)
    if ctx.dry_run:
        ctx.log.info("[dry-run] would scan source for secret patterns")
    elif findings:
        for f in findings:
            ctx.log.error("Possible secret: %s", f)
        failures.append(f"{len(findings)} potential secret(s) found.")
    else:
        ctx.log.info("Secret scan: no findings.")

    # 3) env validation (strict in prod/strict)
    issues = validate_environment(ctx, strict_prod=strict)
    for i in issues:
        (ctx.log.error if i.level == "error" else ctx.log.warning)("%s: %s", i.variable, i.message)
    if has_errors(issues):
        failures.append("Environment validation failed.")

    # 4) bandit (optional, warn-only unless --strict)
    if which("bandit"):
        if ctx.dry_run:
            ctx.log.info("[dry-run] would run: bandit -r app -q")
        else:
            res = run("bandit", "-r", "app", "-q", cwd=ctx.settings.backend_dir)
            print((res.stdout or res.stderr)[-2500:])
            if not res.ok:
                msg = "bandit reported issues."
                if strict:
                    failures.append(msg)
                else:
                    ctx.log.warning("%s (non-blocking; use --strict to fail)", msg)
    else:
        ctx.log.warning("bandit not installed — skipping static analysis (pip install bandit).")

    # 5) Dockerfile sanity
    dockerfile = ctx.settings.dockerfile
    if dockerfile.is_file() and not ctx.dry_run:
        text = dockerfile.read_text(encoding="utf-8", errors="ignore")
        lowered = text.lower()
        if "secret" in lowered and ("arg secret" in lowered or "env secret" in lowered):
            failures.append("Dockerfile appears to bake in secrets (ARG/ENV SECRET).")
        if "user " not in lowered:
            ctx.log.warning("Dockerfile has no USER directive — container may run as root.")

    if failures:
        raise AutomationError("Security checks failed:\n- " + "\n- ".join(failures))
    ctx.log.info("Security checks passed.")
