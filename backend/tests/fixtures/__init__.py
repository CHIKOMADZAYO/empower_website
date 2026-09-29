"""Shared pytest fixtures for backend tests."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture()
def any_client() -> TestClient:
    """Generic app client (alias for `client` in conftest)."""
    return TestClient(create_app())
