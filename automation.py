#!/usr/bin/env python3
"""Centralized automation CLI for the Empower project.

Usage:
    python automation.py setup
    python automation.py format | lint | typecheck
    python automation.py test [--unit | --integration | --api] [--coverage]
    python automation.py db [migrate|upgrade|downgrade|seed|reset]
    python automation.py docker [build|up|down|restart|logs|ps|migrate]
    python automation.py security | build | clean | release | deploy | health | check
    python automation.py <command> --help
    python automation.py build --verbose --dry-run
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from automation.cli.app import main

if __name__ == "__main__":
    raise SystemExit(main())
