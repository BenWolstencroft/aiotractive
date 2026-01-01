"""Tests for the main Tractive client."""

import aiohttp
from aioresponses import aioresponses

from aiotractive import Tractive
from aiotractive.trackable_object import TrackableObject
from aiotractive.tracker import Tracker

API_URL = "https://graph.tractive.com/4"


def mock_auth(m, auth_response):
    m.post(f"{API_URL}/auth/token", payload=auth_response)


async def test_context_manager_closes_session(auth_response):
    with aioresponses() as m:
        mock_auth(m, auth_response)

        async with Tractive("test@example.com", "password") as client:
            await client.authenticate()
            assert client._api.session is not None
            assert not client._api.session.closed

        assert client._api.session.closed


async def test_trackers_list(auth_response, tracker_data):
    with aioresponses() as m:
        mock_auth(m, auth_response)
        m.get(
            f"{API_URL}/user/test_user_123/trackers",
            payload=[tracker_data, {**tracker_data, "_id": "second_tracker"}],
        )

        async with Tractive("test@example.com", "password") as client:
            trackers = await client.trackers()

            assert len(trackers) == 2
            assert all(isinstance(t, Tracker) for t in trackers)
            assert trackers[0]._id == "test_6b3d1679"


async def test_trackable_objects_list(auth_response, trackable_object_data):
    with aioresponses() as m:
        mock_auth(m, auth_response)
        m.get(
            f"{API_URL}/user/test_user_123/trackable_objects",
            payload=[trackable_object_data, {**trackable_object_data, "_id": "second_pet"}],
        )

        async with Tractive("test@example.com", "password") as client:
            objects = await client.trackable_objects()

            assert len(objects) == 2
            assert all(isinstance(o, TrackableObject) for o in objects)
            assert objects[0]._id == "test_a96d8e9c"


async def test_tracker_by_id_no_network_call(auth_response):
    """Getting a tracker by ID should not make any API calls."""
    with aioresponses() as m:
        mock_auth(m, auth_response)

        async with Tractive("test@example.com", "password") as client:
            tracker = client.tracker("some_id")

            assert isinstance(tracker, Tracker)
            assert tracker._id == "some_id"
            assert tracker.type == "tracker"


async def test_trackable_object_by_id_no_network_call(auth_response):
    with aioresponses() as m:
        mock_auth(m, auth_response)

        async with Tractive("test@example.com", "password") as client:
            pet = client.trackable_object("some_pet_id")

            assert isinstance(pet, TrackableObject)
            assert pet._id == "some_pet_id"
            assert pet.type == "pet"


async def test_external_session_not_closed_by_client(auth_response):
    """When using an external session, the client should not close it."""
    with aioresponses() as m:
        mock_auth(m, auth_response)

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with Tractive("test@example.com", "password", session=session) as client:
                await client.authenticate()

            # Session should still be open after Tractive client exits
            assert not session.closed
