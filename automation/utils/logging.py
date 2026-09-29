"""Structured, secret-safe logging.

Why: automation runs shells, docker, DB commands. Logs must be readable
(INFO/WARNING/ERROR/DEBUG), support --verbose, and NEVER leak secrets.
All secret values are redacted via ``redact()`` before output.
"""

from __future__ import annotations

import logging
import re
import sys

_SECRET_KEYS = ("SECRET_KEY", "PASSWORD", "TOKEN", "API_KEY", "DATABASE_URL", "JWT")
_REDACT = re.compile(r"(?i)(secret|password|token|api[_-]?key|authorization)[=: ]\s*\S+")

_logger: logging.Logger | None = None


def redact(message: str) -> str:
    """Redact ``KEY=value`` secrets and bearer tokens from log text."""
    redacted = _REDACT.sub("***redacted***", message)
    for key in _SECRET_KEYS:
        redacted = re.sub(rf"(?i)({key}\s*[=:]\s*)([^\s,;\"']+)", r"\1***", redacted)
    redacted = re.sub(r"(?i)(Bearer\s+)[A-Za-z0-9\-._~+/=]+", r"\1***", redacted)
    return redacted


class SecretFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact(str(record.getMessage()))
        record.args = ()
        return True


def get_logger(name: str = "automation", verbose: bool = False) -> logging.Logger:
    """Return a configured singleton logger (idempotent)."""
    global _logger
    if _logger is not None:
        if verbose:
            _logger.setLevel(logging.DEBUG)
            for h in _logger.handlers:
                h.setLevel(logging.DEBUG)
        return _logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    logger.handlers.clear()
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    handler.setFormatter(logging.Formatter("%(levelname)-7s | %(message)s"))
    handler.addFilter(SecretFilter())
    logger.addHandler(handler)
    logger.propagate = False
    _logger = logger
    return logger


def configure_logging(verbose: bool = False) -> logging.Logger:
    return get_logger(verbose=verbose)
