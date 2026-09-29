"""Automation package entry point (``python -m automation``)."""

from __future__ import annotations

from automation.cli.app import main

if __name__ == "__main__":
    raise SystemExit(main())
