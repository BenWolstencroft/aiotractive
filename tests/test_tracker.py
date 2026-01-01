"""Tests for the Tracker class."""

import json

import pytest
from aresponses import ResponsesMockServer

from aiotractive import Tractive

TRACKER_ID = "test_6b3d1679"


def mock_auth(aresponses, auth_response):
    """Add auth endpoint mock."""
    aresponses.add(
        "graph.tractive.com",
        "/4/auth/token",
        "POST",
        aresponses.Response(body=json.dumps(auth_response), content_type="application/json"),
    )


class TestTrackerDetails:

    async def test_details(self, aresponses: ResponsesMockServer, auth_response, tracker_details):
        mock_auth(aresponses, auth_response)
        aresponses.add(
            "graph.tractive.com",
            f"/4/tracker/{TRACKER_ID}",
            "GET",
            aresponses.Response(body=json.dumps(tracker_details), content_type="application/json"),
        )

        async with Tractive("test@example.com", "password") as client:
            details = await client.tracker(TRACKER_ID).details()

            assert details["_id"] == TRACKER_ID
            assert details["state"] == "OPERATIONAL"
            assert details["battery_state"] == "REGULAR"
            assert "BUZZER" in details["capabilities"]

    async def test_hw_info(self, aresponses: ResponsesMockServer, auth_response, hw_info):
        mock_auth(aresponses, auth_response)
        aresponses.add(
            "graph.tractive.com",
            f"/4/device_hw_report/{TRACKER_ID}/",
            "GET",
            aresponses.Response(body=json.dumps(hw_info), content_type="application/json"),
        )

        async with Tractive("test@example.com", "password") as client:
            info = await client.tracker(TRACKER_ID).hw_info()

            assert info["battery_level"] == 42
            assert info["_type"] == "device_hw_report"

    async def test_pos_report(self, aresponses: ResponsesMockServer, auth_response, pos_report):
        mock_auth(aresponses, auth_response)
        aresponses.add(
            "graph.tractive.com",
            f"/4/device_pos_report/{TRACKER_ID}",
            "GET",
            aresponses.Response(body=json.dumps(pos_report), content_type="application/json"),
        )

        async with Tractive("test@example.com", "password") as client:
            report = await client.tracker(TRACKER_ID).pos_report()

            assert report["latlong"] == [51.5074, -0.1278]
            assert report["sensor_used"] == "KNOWN_WIFI"
            assert report["altitude"] == 149

    async def test_positions_history(self, aresponses: ResponsesMockServer, auth_response, positions_history):
        mock_auth(aresponses, auth_response)
        aresponses.add(
            "graph.tractive.com",
            f"/4/tracker/{TRACKER_ID}/positions",
            "GET",
            aresponses.Response(body=json.dumps(positions_history), content_type="application/json"),
        )

        async with Tractive("test@example.com", "password") as client:
            positions = await client.tracker(TRACKER_ID).positions(1609455600, 1609459200, "json_segments")

            # Response is nested: list of segments, each segment is list of positions
            assert len(positions) == 1
            assert len(positions[0]) == 2
            assert positions[0][0]["latlong"] == [51.5074, -0.1278]


class TestTrackerCommands:

    @pytest.mark.parametrize("active,action", [(True, "on"), (False, "off")])
    async def test_buzzer_control(self, aresponses: ResponsesMockServer, auth_response, active, action):
        mock_auth(aresponses, auth_response)
        aresponses.add(
            "graph.tractive.com",
            f"/4/tracker/{TRACKER_ID}/command/buzzer_control/{action}",
            "GET",
            aresponses.Response(body=json.dumps({"pending": True}), content_type="application/json"),
        )

        async with Tractive("test@example.com", "password") as client:
            result = await client.tracker(TRACKER_ID).set_buzzer_active(active)
            assert result["pending"] is True

    async def test_led_control(self, aresponses: ResponsesMockServer, auth_response):
        mock_auth(aresponses, auth_response)
        aresponses.add(
            "graph.tractive.com",
            f"/4/tracker/{TRACKER_ID}/command/led_control/on",
            "GET",
            aresponses.Response(body=json.dumps({"pending": True}), content_type="application/json"),
        )

        async with Tractive("test@example.com", "password") as client:
            result = await client.tracker(TRACKER_ID).set_led_active(True)
            assert result["pending"] is True

    async def test_live_tracking(self, aresponses: ResponsesMockServer, auth_response):
        mock_auth(aresponses, auth_response)
        aresponses.add(
            "graph.tractive.com",
            f"/4/tracker/{TRACKER_ID}/command/live_tracking/on",
            "GET",
            aresponses.Response(body=json.dumps({"pending": True}), content_type="application/json"),
        )

        async with Tractive("test@example.com", "password") as client:
            result = await client.tracker(TRACKER_ID).set_live_tracking_active(True)
            assert result["pending"] is True


class TestTrackerRepr:

    async def test_repr(self, aresponses: ResponsesMockServer, auth_response):
        mock_auth(aresponses, auth_response)

        async with Tractive("test@example.com", "password") as client:
            tracker = client.tracker(TRACKER_ID)
            assert repr(tracker) == f"<Tracker id={TRACKER_ID} type=tracker>"
