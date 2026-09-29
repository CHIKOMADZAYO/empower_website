"""Terminal output helpers (color, steps, tables) — no third-party deps."""

from __future__ import annotations

RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
DIM = "\033[2m"

import shutil
import sys


def _supports_color() -> bool:
    return sys.stdout.isatty()


def color(text: str, code: str) -> str:
    return f"{code}{text}{RESET}" if _supports_color() else text


def ok(msg: str) -> str:
    return color(f"✔ {msg}", GREEN)


def fail(msg: str) -> str:
    return color(f"✖ {msg}", RED)


def warn(msg: str) -> str:
    return color(f"! {msg}", YELLOW)


def info(msg: str) -> str:
    return color(msg, CYAN)


def header(title: str) -> str:
    width = min(shutil.get_terminal_size((80, 20)).columns, 80)
    bar = "=" * width
    return f"\n{color(bar, DIM)}\n{color(BOLD + title + RESET, '')}\n{color(bar, DIM)}"


def step(number: int, total: int, name: str) -> str:
    return color(f"\n[{number}/{total}] {name}", BOLD + CYAN)
