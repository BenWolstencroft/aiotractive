"""Tests for the Tracker class."""

from __future__ import annotations

import re
from typing import Any

import pytest
from aioresponses import aioresponses

from aiotractive import Tractive
from aiotractive.api import API

TRACKER_ID = "test_6b3d1679"
API_URL = str(API.API_URL)


def mock_auth(mock: aioresponses, auth_response: dict[str, Any]) -> None:
    """Add auth endpoint mock."""
    mock.post(f"{API_URL}auth/token", payload=auth_response)


async def test_tracker_details(
    auth_response: dict[str, Any],
    tracker_details: dict[str, Any],
) -> None:
    """Test fetching tracker details returns device state and capabilities."""
    with aioresponses() as mock:
        mock_auth(mock, auth_response)
        mock.get(f"{API_URL}tracker/{TRACKER_ID}", payload=tracker_details)

        async with Tractive("test@example.com", "password") as client:
            details = await client.tracker(TRACKER_ID).details()

            assert details["_id"] == TRACKER_ID
            assert details["state"] == "OPERATIONAL"
            assert details["battery_state"] == "REGULAR"
            assert "BUZZER" in details["capabilities"]


async def test_tracker_hw_info(
    auth_response: dict[str, Any],
    hw_info: dict[str, Any],
) -> None:
    """Test fetching hardware info returns battery level and device type."""
    with aioresponses() as mock:
        mock_auth(mock, auth_response)
        mock.get(f"{API_URL}device_hw_report/{TRACKER_ID}/", payload=hw_info)

        async with Tractive("test@example.com", "password") as client:
            info = await client.tracker(TRACKER_ID).hw_info()

            assert info["battery_level"] == 42
            assert info["_type"] == "device_hw_report"


async def test_tracker_pos_report(
    auth_response: dict[str, Any],
    pos_report: dict[str, Any],
) -> None:
    """Test fetching position report returns location and sensor data."""
    with aioresponses() as mock:
        mock_auth(mock, auth_response)
        mock.get(f"{API_URL}device_pos_report/{TRACKER_ID}", payload=pos_report)

        async with Tractive("test@example.com", "password") as client:
            report = await client.tracker(TRACKER_ID).pos_report()

            assert report["latlong"] == [51.5074, -0.1278]
            assert report["sensor_used"] == "KNOWN_WIFI"
            assert report["altitude"] == 149


async def test_tracker_positions_history(
    auth_response: dict[str, Any],
    positions_history: list[list[dict[str, Any]]],
) -> None:
    """Test fetching position history returns nested segments of positions."""
    with aioresponses() as mock:
        mock_auth(mock, auth_response)
        pattern = re.compile(
            rf"^{re.escape(API_URL)}tracker/{TRACKER_ID}/positions\?.*$"
        )
        mock.get(pattern, payload=positions_history)

        async with Tractive("test@example.com", "password") as client:
            positions = await client.tracker(TRACKER_ID).positions(
                1609455600, 1609459200, "json_segments"
            )

            # Response is nested: list of segments, each segment is list of positions
            assert len(positions) == 1
            assert len(positions[0]) == 2  # type: ignore[index]
            assert positions[0][0]["latlong"] == [51.5074, -0.1278]  # type: ignore[index]


@pytest.mark.parametrize(("active", "action"), [(True, "on"), (False, "off")])
async def test_tracker_buzzer_control(
    auth_response: dict[str, Any],
    active: bool,
    action: str,
) -> None:
    """Test buzzer control sends correct on/off command."""
    with aioresponses() as mock:
        mock_auth(mock, auth_response)
        mock.get(
            f"{API_URL}tracker/{TRACKER_ID}/command/buzzer_control/{action}",
            payload={"pending": True},
        )

        async with Tractive("test@example.com", "password") as client:
            result = await client.tracker(TRACKER_ID).set_buzzer_active(active)
            assert result["pending"] is True


async def test_tracker_led_control(auth_response: dict[str, Any]) -> None:
    """Test LED control sends correct command to tracker."""
    with aioresponses() as mock:
        mock_auth(mock, auth_response)
        mock.get(
            f"{API_URL}tracker/{TRACKER_ID}/command/led_control/on",
            payload={"pending": True},
        )

        async with Tractive("test@example.com", "password") as client:
            result = await client.tracker(TRACKER_ID).set_led_active(True)
            assert result["pending"] is True


async def test_tracker_live_tracking(auth_response: dict[str, Any]) -> None:
    """Test live tracking activation sends correct command."""
    with aioresponses() as mock:
        mock_auth(mock, auth_response)
        mock.get(
            f"{API_URL}tracker/{TRACKER_ID}/command/live_tracking/on",
            payload={"pending": True},
        )

        async with Tractive("test@example.com", "password") as client:
            result = await client.tracker(TRACKER_ID).set_live_tracking_active(True)
            assert result["pending"] is True


async def test_tracker_repr(auth_response: dict[str, Any]) -> None:
    """Test Tracker string representation includes id and type."""
    with aioresponses() as mock:
        mock_auth(mock, auth_response)

        async with Tractive("test@example.com", "password") as client:
            tracker = client.tracker(TRACKER_ID)
            assert repr(tracker) == f"<Tracker id={TRACKER_ID} type=tracker>"
