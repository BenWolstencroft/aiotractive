"""Tests for the TrackableObject (pet) class."""

from __future__ import annotations

from typing import Any

from aioresponses import aioresponses

from aiotractive import Tractive
from aiotractive.api import API

PET_ID = "test_a96d8e9c"
API_URL = str(API.API_URL)
APS_API_URL = str(API.APS_API_URL)


def mock_auth(mock: aioresponses, auth_response: dict[str, Any]) -> None:
    """Add authentication endpoint mock to aioresponses."""
    mock.post(f"{API_URL}auth/token", payload=auth_response)


async def test_trackable_object_details(
    auth_response: dict[str, Any],
    pet_details: dict[str, Any],
) -> None:
    """Test fetching trackable object details returns pet information."""
    with aioresponses() as mock:
        mock_auth(mock, auth_response)
        mock.get(f"{API_URL}trackable_object/{PET_ID}", payload=pet_details)

        async with Tractive("test@example.com", "password") as client:
            details = await client.trackable_object(PET_ID).details()

            assert details["_id"] == PET_ID
            assert details["details"]["name"] == "Anonymous"
            assert details["details"]["pet_type"] == "DOG"
            assert details["home_location"] == [51.5074, -0.1278]


async def test_trackable_object_health_overview(
    auth_response: dict[str, Any],
    health_overview: dict[str, Any],
) -> None:
    """Health data comes from the APS API (different base URL)."""
    with aioresponses() as mock:
        mock_auth(mock, auth_response)
        mock.get(f"{APS_API_URL}pet/{PET_ID}/health/overview", payload=health_overview)

        async with Tractive("test@example.com", "password") as client:
            health = await client.trackable_object(PET_ID).health_overview()

            assert health["activity"]["minutesActive"] == 418
            assert health["sleep"]["minutesDaySleep"] == 237
            assert health["restingHeartRate"]["status"] == "NORMAL"


async def test_trackable_object_repr(auth_response: dict[str, Any]) -> None:
    """Test TrackableObject string representation includes id and type."""
    with aioresponses() as mock:
        mock_auth(mock, auth_response)

        async with Tractive("test@example.com", "password") as client:
            pet = client.trackable_object(PET_ID)
            assert repr(pet) == f"<TrackableObject id={PET_ID} type=pet>"
