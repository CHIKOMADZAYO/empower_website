"""Tests for env validation + CLI wiring (fast, no docker/network)."""

from __future__ import annotations

import os

from automation.cli.app import build_parser, main
from automation.config.settings import Settings
from automation.infrastructure.context import AppContext
from automation.services.env_service import has_errors, validate_environment


def _ctx(**env: str) -> AppContext:
    for k, v in env.items():
        os.environ[k] = v
    return AppContext(settings=Settings(environment=env.get("ENVIRONMENT", "development")))


def test_dev_defaults_warn_but_no_errors(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("SECRET_KEY", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("ENVIRONMENT", "development")
    ctx = AppContext(
        settings=Settings(
            project_root=tmp_path, environment="development", database_url="", secret_key=""
        )
    )
    issues = validate_environment(ctx)
    assert not has_errors(issues)


def test_production_requires_strong_secret(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    ctx = AppContext(
        settings=Settings(
            project_root=tmp_path,
            environment="production",
            database_url="sqlite:///./x.db",
            secret_key="short",
        )
    )
    issues = validate_environment(ctx, strict_prod=True)
    assert has_errors(issues)
    assert any(i.variable == "SECRET_KEY" for i in issues)


def test_production_rejects_sqlite(tmp_path):
    ctx = AppContext(
        settings=Settings(
            project_root=tmp_path,
            environment="production",
            database_url="sqlite:///./x.db",
            secret_key="a" * 40,
        )
    )
    issues = validate_environment(ctx, strict_prod=True)
    assert any(i.variable == "DATABASE_URL" for i in issues)


def test_cli_parses_core_commands():
    parser = build_parser()
    for argv in (
        ["test", "--unit"],
        ["db", "upgrade"],
        ["docker", "ps"],
        ["health"],
        ["check"],
        ["build", "--skip-docker"],
    ):
        args = parser.parse_args(argv)
        assert args.command in ("test", "db", "docker", "health", "check", "build")


def test_dry_run_clean_and_health_ok(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert main(["--dry-run", "clean"]) == 0
    assert main(["--dry-run", "health", "--url", "http://localhost:8000/api/v1/health"]) == 0


def test_db_migrate_requires_message():
    parser = build_parser()
    try:
        parser.parse_args(["db", "migrate"])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("expected argparse error for missing --message")
