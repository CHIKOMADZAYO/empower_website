"""`clean` — remove generated files."""

from __future__ import annotations

import argparse
import shutil

from automation.infrastructure.context import AppContext

name = "clean"
help = "Remove generated files (__pycache__, caches, dist, coverage)."


def register(sub: argparse._SubParsersAction) -> argparse.ArgumentParser:
    p = sub.add_parser(name, help=help, description=help)
    p.add_argument("--include-db", action="store_true", help="Also remove local dev sqlite files.")
    return p


def run(args: argparse.Namespace, ctx: AppContext) -> int:
    import os

    root = ctx.settings.project_root
    names = {
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "htmlcov",
        ".coverage",
        "coverage.xml",
        "dist",
    }
    skip_dirs = {".git", ".venv", "venv", "node_modules", "frontend"}
    removed = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs and not d.startswith(".git")]
        for d in list(dirnames):
            if d in names:
                full = os.path.join(dirpath, d)
                if ctx.dry_run:
                    ctx.log.info("[dry-run] would remove %s", full)
                else:
                    shutil.rmtree(full, ignore_errors=True)
                    removed += 1
                dirnames.remove(d)
        for f in filenames:
            if f in names:
                full = os.path.join(dirpath, f)
                if ctx.dry_run:
                    ctx.log.info("[dry-run] would remove %s", full)
                else:
                    try:
                        os.unlink(full)
                        removed += 1
                    except OSError:
                        pass
    if args.include_db:
        for db in (root / "backend" / "empower.db", root / "backend" / "data" / "empower.db"):
            if db.is_file():
                if ctx.dry_run:
                    ctx.log.info("[dry-run] would remove %s", db)
                else:
                    db.unlink()
                    removed += 1
    ctx.log.info("Clean done (%d entries).", removed)
    return 0
