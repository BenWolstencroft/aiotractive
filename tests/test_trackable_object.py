"""Tests for the TrackableObject (pet) class."""

import json

import pytest
from aresponses import ResponsesMockServer

from aiotractive import Tractive

PET_ID = "test_a96d8e9c"


def mock_auth(aresponses, auth_response):
    aresponses.add(
        "graph.tractive.com",
        "/4/auth/token",
        "POST",
        aresponses.Response(body=json.dumps(auth_response), content_type="application/json"),
    )


async def test_trackable_object_details(aresponses: ResponsesMockServer, auth_response, pet_details):
    mock_auth(aresponses, auth_response)
    aresponses.add(
        "graph.tractive.com",
        f"/4/trackable_object/{PET_ID}",
        "GET",
        aresponses.Response(body=json.dumps(pet_details), content_type="application/json"),
    )

    async with Tractive("test@example.com", "password") as client:
        details = await client.trackable_object(PET_ID).details()

        assert details["_id"] == PET_ID
        assert details["details"]["name"] == "Anonymous"
        assert details["details"]["pet_type"] == "DOG"
        assert details["home_location"] == [51.5074, -0.1278]


async def test_trackable_object_health_overview(aresponses: ResponsesMockServer, auth_response, health_overview):
    """Health data comes from the APS API (different base URL)."""
    mock_auth(aresponses, auth_response)
    aresponses.add(
        "aps-api.tractive.com",
        f"/api/1/pet/{PET_ID}/health/overview",
        "GET",
        aresponses.Response(body=json.dumps(health_overview), content_type="application/json"),
    )

    async with Tractive("test@example.com", "password") as client:
        health = await client.trackable_object(PET_ID).health_overview()

        assert health["activity"]["minutesActive"] == 418
        assert health["sleep"]["minutesDaySleep"] == 237
        assert health["restingHeartRate"]["status"] == "NORMAL"


async def test_trackable_object_repr(aresponses: ResponsesMockServer, auth_response):
    mock_auth(aresponses, auth_response)

    async with Tractive("test@example.com", "password") as client:
        pet = client.trackable_object(PET_ID)
        assert repr(pet) == f"<TrackableObject id={PET_ID} type=pet>"
