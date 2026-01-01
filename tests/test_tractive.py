"""Tests for the main Tractive client."""

import json

import aiohttp
import pytest
from aresponses import ResponsesMockServer

from aiotractive import Tractive
from aiotractive.trackable_object import TrackableObject
from aiotractive.tracker import Tracker


def mock_auth(aresponses, auth_response):
    aresponses.add(
        "graph.tractive.com",
        "/4/auth/token",
        "POST",
        aresponses.Response(body=json.dumps(auth_response), content_type="application/json"),
    )


async def test_context_manager_closes_session(aresponses: ResponsesMockServer, auth_response):
    mock_auth(aresponses, auth_response)

    async with Tractive("test@example.com", "password") as client:
        await client.authenticate()
        assert client._api.session is not None
        assert not client._api.session.closed

    assert client._api.session.closed


async def test_trackers_list(aresponses: ResponsesMockServer, auth_response, tracker_data):
    mock_auth(aresponses, auth_response)
    aresponses.add(
        "graph.tractive.com",
        "/4/user/test_user_123/trackers",
        "GET",
        aresponses.Response(
            body=json.dumps([tracker_data, {**tracker_data, "_id": "second_tracker"}]),
            content_type="application/json",
        ),
    )

    async with Tractive("test@example.com", "password") as client:
        trackers = await client.trackers()

        assert len(trackers) == 2
        assert all(isinstance(t, Tracker) for t in trackers)
        assert trackers[0]._id == "test_6b3d1679"


async def test_trackable_objects_list(aresponses: ResponsesMockServer, auth_response, trackable_object_data):
    mock_auth(aresponses, auth_response)
    aresponses.add(
        "graph.tractive.com",
        "/4/user/test_user_123/trackable_objects",
        "GET",
        aresponses.Response(
            body=json.dumps([trackable_object_data, {**trackable_object_data, "_id": "second_pet"}]),
            content_type="application/json",
        ),
    )

    async with Tractive("test@example.com", "password") as client:
        objects = await client.trackable_objects()

        assert len(objects) == 2
        assert all(isinstance(o, TrackableObject) for o in objects)
        assert objects[0]._id == "test_a96d8e9c"


async def test_tracker_by_id_no_network_call(aresponses: ResponsesMockServer, auth_response):
    """Getting a tracker by ID should not make any API calls."""
    mock_auth(aresponses, auth_response)

    async with Tractive("test@example.com", "password") as client:
        tracker = client.tracker("some_id")

        assert isinstance(tracker, Tracker)
        assert tracker._id == "some_id"
        assert tracker.type == "tracker"


async def test_trackable_object_by_id_no_network_call(aresponses: ResponsesMockServer, auth_response):
    mock_auth(aresponses, auth_response)

    async with Tractive("test@example.com", "password") as client:
        pet = client.trackable_object("some_pet_id")

        assert isinstance(pet, TrackableObject)
        assert pet._id == "some_pet_id"
        assert pet.type == "pet"


async def test_external_session_not_closed_by_client(aresponses: ResponsesMockServer, auth_response):
    """When using an external session, the client should not close it."""
    mock_auth(aresponses, auth_response)

    async with aiohttp.ClientSession(raise_for_status=True) as session:
        async with Tractive("test@example.com", "password", session=session) as client:
            await client.authenticate()

        # Session should still be open after Tractive client exits
        assert not session.closed
