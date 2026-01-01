"""Tests for the API client."""

import json

import pytest
from aresponses import ResponsesMockServer

from aiotractive import Tractive
from aiotractive.exceptions import NotFoundError, TractiveError, UnauthorizedError


def mock_auth(aresponses, auth_response):
    aresponses.add(
        "graph.tractive.com",
        "/4/auth/token",
        "POST",
        aresponses.Response(body=json.dumps(auth_response), content_type="application/json"),
    )


async def test_auth_success(aresponses: ResponsesMockServer, auth_response):
    mock_auth(aresponses, auth_response)

    async with Tractive("test@example.com", "password") as client:
        creds = await client.authenticate()

        assert creds["user_id"] == "test_user_123"
        assert creds["access_token"] == "test_access_token_xyz"


async def test_auth_caches_credentials(aresponses: ResponsesMockServer, auth_response):
    mock_auth(aresponses, auth_response)

    async with Tractive("test@example.com", "password") as client:
        creds1 = await client.authenticate()
        creds2 = await client.authenticate()
        assert creds1 is creds2  # Same object, not a new request


@pytest.mark.parametrize("status", [401, 403])
async def test_auth_invalid_credentials(aresponses: ResponsesMockServer, status):
    aresponses.add("graph.tractive.com", "/4/auth/token", "POST", aresponses.Response(status=status))

    async with Tractive("test@example.com", "wrong") as client:
        with pytest.raises(UnauthorizedError):
            await client.authenticate()


async def test_request_404_raises_not_found(aresponses: ResponsesMockServer, auth_response):
    mock_auth(aresponses, auth_response)
    aresponses.add("graph.tractive.com", "/4/tracker/bad_id", "GET", aresponses.Response(status=404))

    async with Tractive("test@example.com", "password") as client:
        with pytest.raises(NotFoundError):
            await client.tracker("bad_id").details()


async def test_request_500_raises_tractive_error(aresponses: ResponsesMockServer, auth_response):
    mock_auth(aresponses, auth_response)
    aresponses.add("graph.tractive.com", "/4/tracker/test123", "GET", aresponses.Response(status=500))

    async with Tractive("test@example.com", "password") as client:
        with pytest.raises(TractiveError):
            await client.tracker("test123").details()


async def test_request_429_raises_tractive_error(aresponses: ResponsesMockServer, auth_response):
    """
    Rate limiting (429) currently raises TractiveError instead of retrying.
    The retry logic doesn't work because raise_for_status=True throws before
    we can check the status code.
    """
    mock_auth(aresponses, auth_response)
    aresponses.add("graph.tractive.com", "/4/tracker/test123", "GET", aresponses.Response(status=429))

    async with Tractive("test@example.com", "password") as client:
        with pytest.raises(TractiveError):
            await client.tracker("test123").details()


async def test_user_id(aresponses: ResponsesMockServer, auth_response):
    mock_auth(aresponses, auth_response)

    async with Tractive("test@example.com", "password") as client:
        assert await client._api.user_id() == "test_user_123"


async def test_auth_headers(aresponses: ResponsesMockServer, auth_response):
    mock_auth(aresponses, auth_response)

    async with Tractive("test@example.com", "password") as client:
        headers = await client._api.auth_headers()

        assert headers["authorization"] == "Bearer test_access_token_xyz"
        assert headers["x-tractive-user"] == "test_user_123"
