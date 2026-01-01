"""Shared pytest fixtures for aiotractive tests.

These fixtures are based on real anonymized API responses from the Tractive API.
Fixture data is stored in JSON files in the fixtures/ directory.
"""

import json
from pathlib import Path
from typing import Any

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> Any:
    """Load a fixture from a JSON file."""
    with open(FIXTURES_DIR / f"{name}.json", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def auth_response() -> dict[str, Any]:
    """Standard authentication response."""
    return load_fixture("auth_response")


@pytest.fixture
def tracker_data() -> dict[str, Any]:
    """Standard tracker data from trackers list endpoint."""
    return load_fixture("tracker_data")


@pytest.fixture
def trackable_object_data() -> dict[str, Any]:
    """Standard trackable object (pet) data from list endpoint."""
    return load_fixture("trackable_object_data")


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
