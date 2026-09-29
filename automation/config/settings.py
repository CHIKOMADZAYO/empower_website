"""Central configuration: paths, env vars, defaults.

Problem solved: every command needs the same project root, backend dir,
env file locations and required variables. Without this, each command
re-implements path/env logic (DRY violation) and drifts.

Pattern: Simple Settings object + Dependency Injection. Commands receive
a ``Settings`` / ``AppContext`` instead of reading ``os.environ`` directly,
which makes them testable and keeps I/O at the edges (Clean Architecture).
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def find_project_root(
    marker_files: tuple[str, ...] = ("pyproject.toml", ".git", "automation.py"),
) -> Path:
    """Walk up from this file until a project marker is found."""
    here = Path(__file__).resolve()
    for parent in (here.parent, *here.parents):
        for marker in marker_files:
            if (parent / marker).exists():
                return parent
    # Fallback: repo root is two levels above automation/config/
    return here.parents[2] if len(here.parents) >= 3 else here.parent


@dataclass(frozen=True)
class Settings:
    """Immutable runtime settings. Override via env vars or CLI flags."""

    project_root: Path = field(default_factory=find_project_root)
    environment: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    database_url: str = field(default_factory=lambda: os.getenv("DATABASE_URL", ""))
    secret_key: str = field(
        default_factory=lambda: os.getenv("SECRET_KEY", os.getenv("EMPOWER_SECRET_KEY", ""))
    )
    redis_url: str = field(
        default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379/0")
    )
    verbose: bool = False

    @property
    def backend_dir(self) -> Path:
        return self.project_root / "backend"

    @property
    def frontend_dir(self) -> Path:
        return self.project_root / "frontend"

    @property
    def env_file(self) -> Path:
        return self.project_root / ".env"

    @property
    def env_example(self) -> Path:
        return self.project_root / ".env.example"

    @property
    def backend_env_example(self) -> Path:
        return self.backend_dir / ".env.example"

    @property
    def compose_file(self) -> Path:
        return self.project_root / "docker-compose.yml"

    @property
    def dockerfile(self) -> Path:
        return self.project_root / "Dockerfile"


# (name, required_in_prod, description)
REQUIRED_VARS: tuple[tuple[str, bool, str], ...] = (
    ("DATABASE_URL", True, "SQLAlchemy database URL (e.g. postgresql+psycopg://...)"),
    ("SECRET_KEY", True, "JWT signing secret (min 32 chars in prod)"),
    ("ENVIRONMENT", False, "development | staging | production"),
    ("REDIS_URL", False, "Redis URL for cache/rate-limit"),
)

# External services checked by `setup --check-services` (host, port, label).
REQUIRED_SERVICES: tuple[tuple[str, int, str], ...] = (
    ("localhost", 5432, "PostgreSQL"),
    ("localhost", 6379, "Redis (optional)"),
)


def load_dotenv_if_present(env_file: Path) -> None:
    """Minimal .env loader (no third-party dep) — never overrides real env."""
    if not env_file.is_file():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip("'\"")
        os.environ.setdefault(key, value)
