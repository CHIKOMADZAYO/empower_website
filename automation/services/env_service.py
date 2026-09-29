"""Environment/config validation service.

Solves: 'works on my machine' — missing .env, weak SECRET_KEY, bad DATABASE_URL.
Used by setup, build (fail-fast), deploy (gate), and CI.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass

from automation.config.settings import REQUIRED_VARS, Settings, load_dotenv_if_present
from automation.infrastructure.context import AppContext

MIN_SECRET_LEN_PROD = 32


@dataclass(frozen=True)
class ValidationIssue:
    level: str  # "error" | "warning"
    variable: str
    message: str


def validate_environment(ctx: AppContext, *, strict_prod: bool = False) -> list[ValidationIssue]:
    """Validate env vars. Returns issues; empty list == valid."""
    settings: Settings = ctx.settings
    load_dotenv_if_present(settings.env_file)
    # Re-read live env (load_dotenv only filled missing values).
    env = {
        "DATABASE_URL": os.getenv("DATABASE_URL", settings.database_url),
        "SECRET_KEY": os.getenv("SECRET_KEY", os.getenv("EMPOWER_SECRET_KEY", settings.secret_key)),
        "ENVIRONMENT": os.getenv("ENVIRONMENT", settings.environment),
        "REDIS_URL": os.getenv("REDIS_URL", settings.redis_url),
    }
    is_prod = (env["ENVIRONMENT"] or "").lower() == "production" or strict_prod
    issues: list[ValidationIssue] = []

    for name, required_in_prod, _desc in REQUIRED_VARS:
        value = env.get(name, "")
        if not value:
            if required_in_prod and is_prod:
                issues.append(
                    ValidationIssue(
                        "error", name, f"{name} is required in production but is missing/empty."
                    )
                )
            elif name in ("DATABASE_URL", "SECRET_KEY"):
                issues.append(
                    ValidationIssue(
                        "warning", name, f"{name} is empty; using built-in dev default."
                    )
                )
            continue
        if name == "SECRET_KEY" and (is_prod or strict_prod):
            weak = {"development-only-change-me", "change-me", "secret", "test", "dev"}
            if (
                len(value) < MIN_SECRET_LEN_PROD
                or value.lower() in weak
                or "change" in value.lower()
            ):
                issues.append(
                    ValidationIssue(
                        "error",
                        name,
                        "SECRET_KEY too weak for production "
                        f"(need >= {MIN_SECRET_LEN_PROD} random chars).",
                    )
                )
        if name == "DATABASE_URL" and is_prod and value.startswith("sqlite"):
            issues.append(
                ValidationIssue(
                    "error",
                    name,
                    "SQLite DATABASE_URL is not allowed in production; use PostgreSQL.",
                )
            )
    if sys.version_info < (3, 12):  # noqa: UP036 - runtime guard for older interpreters
        issues.append(
            ValidationIssue(
                "warning",
                "PYTHON",
                f"Python {sys.version.split()[0]} < 3.12; project targets 3.12+.",
            )
        )
    return issues


def has_errors(issues: list[ValidationIssue]) -> bool:
    return any(i.level == "error" for i in issues)
