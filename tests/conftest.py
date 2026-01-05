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
def tracker_details() -> dict[str, Any]:
    """Real API response structure for tracker details (anonymized)."""
    return load_fixture("tracker_details")  # type: ignore[return-value]


@pytest.fixture
def hw_info() -> dict[str, Any]:
    """Real API response structure for hardware info (anonymized)."""
    return load_fixture("hw_info")  # type: ignore[return-value]


@pytest.fixture
def pos_report() -> dict[str, Any]:
    """Real API response structure for position report (anonymized)."""
    return load_fixture("pos_report")  # type: ignore[return-value]


@pytest.fixture
def positions_history() -> list[list[dict[str, Any]]]:
    """Real API response structure for positions history (anonymized)."""
    return load_fixture("positions_history")  # type: ignore[return-value]
