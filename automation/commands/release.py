"""`release` — validate, bump version, git tag."""

from __future__ import annotations

import argparse

from automation.infrastructure.context import AppContext, AutomationError
from automation.services.env_service import has_errors, validate_environment
from automation.services.ops_service import bump_version_file, git_checks, git_tag

name = "release"
help = "Tag a release: validate -> version bump -> git tag."


def register(sub: argparse._SubParsersAction) -> argparse.ArgumentParser:
    p = sub.add_parser(name, help=help, description=help)
    p.add_argument("--bump", choices=["patch", "minor", "major"], default="patch")
    p.add_argument("--push", action="store_true", help="Push tags to origin.")
    return p


def run(args: argparse.Namespace, ctx: AppContext) -> int:
    git_checks(ctx)
    if has_errors(validate_environment(ctx)):
        raise AutomationError("Release blocked: environment validation errors.")
    pyproject = ctx.settings.project_root / "pyproject.toml"
    if not pyproject.is_file():
        raise AutomationError("No pyproject.toml at project root; cannot bump version.")
    new = "0.0.0" if ctx.dry_run else bump_version_file(pyproject, args.bump)
    ctx.log.info("Version bumped (%s) -> %s", args.bump, new)
    git_tag(ctx, new)
    if args.push:
        from automation.utils.process import run as _run

        if ctx.dry_run:
            ctx.log.info("[dry-run] would run: git push --tags")
        else:
            res = _run("git", "push", "--tags", cwd=ctx.settings.project_root)
            if not res.ok:
                raise AutomationError("git push --tags failed.", hint=res.stderr[-1000:])
    return 0
