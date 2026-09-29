"""Infrastructure package: cross-cutting runtime concerns."""

from automation.infrastructure.context import (
    AppContext,
    AutomationError,
    PipelineResult,
    StepResult,
)

__all__ = ["AppContext", "AutomationError", "PipelineResult", "StepResult"]
