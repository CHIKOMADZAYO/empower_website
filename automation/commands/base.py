"""Command protocol + registry. Each command: small, focused, injectable.

Pattern: Command (each file exposes ``register(subparsers)`` and a
``run(args, ctx) -> int``). The CLI layer only parses args and builds the
AppContext; services do the work. This keeps commands thin and testable.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable
from typing import Protocol

from automation.infrastructure.context import AppContext


class Command(Protocol):
    name: str
    help: str

    def register(self, subparsers: argparse._SubParsersAction) -> None: ...
    def run(self, args: argparse.Namespace, ctx: AppContext) -> int: ...


Handler = Callable[[argparse.Namespace, AppContext], int]
