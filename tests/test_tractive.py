"""Tests for the main Tractive client."""

from __future__ import annotations

from typing import Any

import aiohttp
from aioresponses import aioresponses

from aiotractive import Tractive
from aiotractive.api import API
from aiotractive.trackable_object import TrackableObject
from aiotractive.tracker import Tracker

API_URL = str(API.API_URL)


def mock_auth(mock: aioresponses, auth_response: dict[str, Any]) -> None:
    """Add authentication endpoint mock to aioresponses."""
    mock.post(f"{API_URL}auth/token", payload=auth_response, repeat=True)


async def test_context_manager_closes_session(auth_response: dict[str, Any]) -> None:
    """Test that exiting context manager closes the HTTP session."""
    with aioresponses() as mock:
        mock_auth(mock, auth_response)

        async with Tractive("test@example.com", "password") as client:
            await client.authenticate()
            assert client._api.session is not None
            assert not client._api.session.closed

        assert client._api.session.closed


async def test_trackers_list(
    auth_response: dict[str, Any],
    tracker_data: dict[str, Any],
) -> None:
    """Test fetching trackers returns list of Tracker objects."""
    with aioresponses() as mock:
        mock_auth(mock, auth_response)
        mock.get(
            f"{API_URL}user/test_user_123/trackers",
            payload=[tracker_data, {**tracker_data, "_id": "second_tracker"}],
        )

        async with Tractive("test@example.com", "password") as client:
            trackers = await client.trackers()

            assert len(trackers) == 2
            assert all(isinstance(t, Tracker) for t in trackers)
            assert trackers[0]._id == "test_6b3d1679"


async def test_trackable_objects_list(
    auth_response: dict[str, Any],
    trackable_object_data: dict[str, Any],
) -> None:
    """Test fetching trackable objects returns list of TrackableObject instances."""
    with aioresponses() as mock:
        mock_auth(mock, auth_response)
        mock.get(
            f"{API_URL}user/test_user_123/trackable_objects",
            payload=[
                trackable_object_data,
                {**trackable_object_data, "_id": "second_pet"},
            ],
        )

        async with Tractive("test@example.com", "password") as client:
            objects = await client.trackable_objects()

            assert len(objects) == 2
            assert all(isinstance(o, TrackableObject) for o in objects)
            assert objects[0]._id == "test_a96d8e9c"


async def test_tracker_by_id_no_network_call(auth_response: dict[str, Any]) -> None:
    """Getting a tracker by ID should not make any API calls."""
    with aioresponses() as mock:
        mock_auth(mock, auth_response)

        async with Tractive("test@example.com", "password") as client:
            tracker = client.tracker("some_id")

            assert isinstance(tracker, Tracker)
            assert tracker._id == "some_id"
            assert tracker.type == "tracker"


async def test_trackable_object_by_id_no_network_call(
    auth_response: dict[str, Any],
) -> None:
    """Test that getting a trackable object by ID does not make API calls."""
    with aioresponses() as mock:
        mock_auth(mock, auth_response)

        async with Tractive("test@example.com", "password") as client:
            pet = client.trackable_object("some_pet_id")

            assert isinstance(pet, TrackableObject)
            assert pet._id == "some_pet_id"
            assert pet.type == "pet"


async def test_external_session_not_closed_by_client(
    auth_response: dict[str, Any],
) -> None:
    """When using an external session, the client should not close it."""
    with aioresponses() as mock:
        mock_auth(mock, auth_response)

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with Tractive(
                "test@example.com", "password", session=session
            ) as client:
                await client.authenticate()

            # Session should still be open after Tractive client exits
            assert not session.closed
