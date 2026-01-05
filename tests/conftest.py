"""Shared pytest fixtures for aiotractive tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> dict[str, Any] | list[Any]:
    """Load a fixture from a JSON file."""
    with (FIXTURES_DIR / f"{name}.json").open(encoding="utf-8") as f:
        return json.load(f)  # type: ignore[no-any-return]


@pytest.fixture
def auth_response() -> dict[str, Any]:
    """Return standard authentication response."""
    return load_fixture("auth_response")  # type: ignore[return-value]


@pytest.fixture
def tracker_data() -> dict[str, Any]:
    """Return tracker data from trackers list endpoint."""
    return load_fixture("tracker_data")  # type: ignore[return-value]


@pytest.fixture
def trackable_object_data() -> dict[str, Any]:
    """Return trackable object (pet) data from list endpoint."""
    return load_fixture("trackable_object_data")  # type: ignore[return-value]
