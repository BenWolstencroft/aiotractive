"""Shared pytest fixtures for aiotractive tests.

These fixtures are based on real anonymized API responses from the Tractive API.
Fixture data is stored in JSON files in the fixtures/ directory.
"""

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


@pytest.fixture
def tracker_details() -> dict[str, Any]:
    """Real API response structure for tracker details (anonymized)."""
    return load_fixture("tracker_details")


@pytest.fixture
def hw_info() -> dict[str, Any]:
    """Real API response structure for hardware info (anonymized)."""
    return load_fixture("hw_info")


@pytest.fixture
def pos_report() -> dict[str, Any]:
    """Real API response structure for position report (anonymized)."""
    return load_fixture("pos_report")


@pytest.fixture
def positions_history() -> list[list[dict[str, Any]]]:
    """Real API response structure for positions history (anonymized)."""
    return load_fixture("positions_history")


@pytest.fixture
def pet_details() -> dict[str, Any]:
    """Real API response structure for trackable object details (anonymized)."""
    return load_fixture("pet_details")


@pytest.fixture
def health_overview() -> dict[str, Any]:
    """Real API response structure for health overview from APS API (anonymized)."""
    return load_fixture("health_overview")
