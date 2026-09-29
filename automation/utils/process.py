"""Subprocess helpers with streaming, timeouts, and safe error reporting."""

from __future__ import annotations

import logging
import shlex
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

log = logging.getLogger("automation")


@dataclass(frozen=True)
class CommandResult:
    command: tuple[str, ...]
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


class CommandError(RuntimeError):
    """Raised when a subprocess exits non-zero and ``check=True``."""

    def __init__(self, result: CommandResult) -> None:
        self.result = result
        super().__init__(
            f"Command failed ({result.returncode}): "
            f"{' '.join(result.command)}\n{result.stderr[-2000:]}"
        )


def which(program: str) -> str | None:
    return shutil.which(program)


def run(
    *args: str,
    cwd: Path | str | None = None,
    env: dict[str, str] | None = None,
    check: bool = False,
    capture: bool = True,
    timeout: int = 600,
) -> CommandResult:
    """Run a command; never prints secrets (callers must redact before logging)."""
    import os as _os

    cmd = tuple(args)
    log.debug("run: %s (cwd=%s)", " ".join(shlex.quote(c) for c in cmd), cwd)
    merged = dict(_os.environ)
    if env:
        merged.update(env)
    try:
        completed = subprocess.run(
            list(cmd),
            cwd=str(cwd) if cwd else None,
            env=merged,
            capture_output=capture,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        raise CommandError(CommandResult(cmd, 127, "", f"program not found: {cmd[0]}")) from exc
    except subprocess.TimeoutExpired as exc:
        raise CommandError(CommandResult(cmd, 124, "", f"timed out after {timeout}s")) from exc
    result = CommandResult(
        cmd, completed.returncode, completed.stdout or "", completed.stderr or ""
    )
    if check and not result.ok:
        raise CommandError(result)
    return result
