"""CLI composition root: argparse wiring, context building, error -> exit code.

Why argparse over click/typer: zero new dependencies, stdlib, explicit help
texts, and easy `--help` per subcommand — matches 'prefer modern practices,
avoid unnecessary dependencies'.
"""

from __future__ import annotations

import argparse
import sys
import traceback

from automation import __version__
from automation.commands import (
    build,
    clean,
    db,
    deploy,
    docker,
    ops,
    quality,
    release,
    security,
    setup,
    test,
)
from automation.config.settings import Settings, load_dotenv_if_present
from automation.infrastructure.context import AppContext, AutomationError
from automation.utils.logging import configure_logging
from automation.utils.output import fail
from automation.utils.process import CommandError

EXIT_OK, EXIT_ERROR, EXIT_USAGE = 0, 1, 2


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="automation.py",
        description=(
            "Empower automation CLI — setup, quality, tests, DB, Docker, security, build, deploy."
        ),
        epilog=(
            "Examples: python automation.py setup | "
            "python automation.py test --unit | python automation.py db reset --force"
        ),
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    p.add_argument("--verbose", action="store_true", help="DEBUG logging.")
    p.add_argument("--dry-run", action="store_true", help="Print what would run without executing.")
    p.add_argument(
        "--force", action="store_true", help="Skip confirmations for destructive commands."
    )
    sub = p.add_subparsers(dest="command", required=True, metavar="COMMAND")

    setup.register(sub)
    for _cname, _chelp, reg, _run in quality.COMMANDS:
        reg(sub)
    test.register(sub)
    db.register(sub)
    docker.register(sub)
    security.register(sub)
    build.register(sub)
    clean.register(sub)
    release.register(sub)
    deploy.register(sub)
    for _cname, _chelp, reg, _run in ops.COMMANDS:
        reg(sub)
    return p


_HANDLERS = {
    "setup": setup.run,
    "test": test.run,
    "db": db.run,
    "docker": docker.run,
    "security": security.run,
    "build": build.run,
    "clean": clean.run,
    "release": release.run,
    "deploy": deploy.run,
}
for _cname, _chelp, _reg, _run in (*quality.COMMANDS, *ops.COMMANDS):
    _HANDLERS[_cname] = _run


def build_context(args: argparse.Namespace) -> AppContext:
    root_settings = Settings(verbose=bool(args.verbose))
    load_dotenv_if_present(root_settings.env_file)
    load_dotenv_if_present(root_settings.backend_dir / ".env")
    settings = Settings(verbose=bool(args.verbose))  # re-read after dotenv
    return AppContext(
        settings=settings,
        dry_run=bool(args.dry_run),
        force=bool(args.force),
        verbose=bool(args.verbose),
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    log = configure_logging(verbose=bool(args.verbose))
    try:
        ctx = build_context(args)
    except Exception as exc:
        print(fail(f"Failed to load configuration: {exc}"), file=sys.stderr)
        return EXIT_USAGE
    handler = _HANDLERS.get(args.command)
    if handler is None:
        parser.print_help()
        return EXIT_USAGE
    try:
        return int(handler(args, ctx) or 0)
    except AutomationError as exc:
        log.error("%s", exc)
        if exc.hint:
            log.info("Hint: %s", exc.hint[-1500:])
        return EXIT_ERROR
    except CommandError as exc:
        log.error("%s", exc)
        return EXIT_ERROR
    except KeyboardInterrupt:
        log.warning("Interrupted by user.")
        return 130
    except Exception as exc:  # unexpected: traceback only in verbose
        log.error("Unexpected error: %s: %s", type(exc).__name__, exc)
        if args.verbose:
            traceback.print_exc()
        else:
            log.info("Re-run with --verbose for a traceback.")
        return EXIT_ERROR
