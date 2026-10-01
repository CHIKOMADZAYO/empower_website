"""Canonical roles used by API authorization."""

from enum import StrEnum


class UserRole(StrEnum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"
