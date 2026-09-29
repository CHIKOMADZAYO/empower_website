"""Shared errors, result types and execution context (Dependency Injection root).

Clean Architecture mapping:
- ``AutomationError`` / ``StepResult`` / ``PipelineResult`` — domain primitives.
- ``AppContext`` — composition root object handed to every command/service,
  carrying Settings + logger + flags (dry_run, force, verbose) so business
  logic never touches globals directly (DIP: depend on abstractions).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from automation.config.settings import Settings
from automation.utils.logging import get_logger


class AutomationError(RuntimeError):
    """Expected, user-facing automation failure (exit code 1)."""

    def __init__(self, message: str, *, hint: str | None = None) -> None:
        self.hint = hint
        super().__init__(message)


@dataclass(frozen=True)
class StepResult:
    name: str
    ok: bool
    detail: str = ""
    duration_s: float = 0.0


@dataclass()
class PipelineResult:
    steps: list[StepResult] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return all(s.ok for s in self.steps)

    @property
    def failed(self) -> list[StepResult]:
        return [s for s in self.steps if not s.ok]

    def add(self, result: StepResult) -> None:
        self.steps.append(result)


@dataclass(frozen=True)
class AppContext:
    """Injected into commands and services. Single Responsibility: carry runtime deps."""

    settings: Settings
    dry_run: bool = False
    force: bool = False
    verbose: bool = False
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def log(self):  # typed loosely to avoid import cycle cost
        return get_logger(verbose=self.verbose)
