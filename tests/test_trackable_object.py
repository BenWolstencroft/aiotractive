"""Tests for the TrackableObject (pet) class."""

from aioresponses import aioresponses

from aiotractive import Tractive

PET_ID = "test_a96d8e9c"
API_URL = "https://graph.tractive.com/4"
APS_API_URL = "https://aps-api.tractive.com/api/1"


def mock_auth(m, auth_response):
    m.post(f"{API_URL}/auth/token", payload=auth_response)


async def test_trackable_object_details(auth_response, pet_details):
    with aioresponses() as m:
        mock_auth(m, auth_response)
        m.get(f"{API_URL}/trackable_object/{PET_ID}", payload=pet_details)

        async with Tractive("test@example.com", "password") as client:
            details = await client.trackable_object(PET_ID).details()

            assert details["_id"] == PET_ID
            assert details["details"]["name"] == "Anonymous"
            assert details["details"]["pet_type"] == "DOG"
            assert details["home_location"] == [51.5074, -0.1278]


async def test_trackable_object_health_overview(auth_response, health_overview):
    """Health data comes from the APS API (different base URL)."""
    with aioresponses() as m:
        mock_auth(m, auth_response)
        m.get(f"{APS_API_URL}/pet/{PET_ID}/health/overview", payload=health_overview)

        async with Tractive("test@example.com", "password") as client:
            health = await client.trackable_object(PET_ID).health_overview()

            assert health["activity"]["minutesActive"] == 418
            assert health["sleep"]["minutesDaySleep"] == 237
            assert health["restingHeartRate"]["status"] == "NORMAL"


async def test_trackable_object_repr(auth_response):
    with aioresponses() as m:
        mock_auth(m, auth_response)

        async with Tractive("test@example.com", "password") as client:
            pet = client.trackable_object(PET_ID)
            assert repr(pet) == f"<TrackableObject id={PET_ID} type=pet>"
