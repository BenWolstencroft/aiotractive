"""Tests for the API client."""

import pytest
from aioresponses import aioresponses

from aiotractive import Tractive
from aiotractive.exceptions import NotFoundError, TractiveError, UnauthorizedError

API_URL = "https://graph.tractive.com/4"


def mock_auth(m, auth_response):
    m.post(f"{API_URL}/auth/token", payload=auth_response)


async def test_auth_success(auth_response):
    with aioresponses() as m:
        mock_auth(m, auth_response)

        async with Tractive("test@example.com", "password") as client:
            creds = await client.authenticate()

            assert creds["user_id"] == "test_user_123"
            assert creds["access_token"] == "test_access_token_xyz"


async def test_auth_caches_credentials(auth_response):
    with aioresponses() as m:
        mock_auth(m, auth_response)

        async with Tractive("test@example.com", "password") as client:
            creds1 = await client.authenticate()
            creds2 = await client.authenticate()
            assert creds1 is creds2  # Same object, not a new request


@pytest.mark.parametrize("status", [401, 403])
async def test_auth_invalid_credentials(status):
    with aioresponses() as m:
        m.post(f"{API_URL}/auth/token", status=status)

        async with Tractive("test@example.com", "wrong") as client:
            with pytest.raises(UnauthorizedError):
                await client.authenticate()


async def test_request_404_raises_not_found(auth_response):
    with aioresponses() as m:
        mock_auth(m, auth_response)
        m.get(f"{API_URL}/tracker/bad_id", status=404)

        async with Tractive("test@example.com", "password") as client:
            with pytest.raises(NotFoundError):
                await client.tracker("bad_id").details()


async def test_request_500_raises_tractive_error(auth_response):
    with aioresponses() as m:
        mock_auth(m, auth_response)
        m.get(f"{API_URL}/tracker/test123", status=500)

        async with Tractive("test@example.com", "password") as client:
            with pytest.raises(TractiveError):
                await client.tracker("test123").details()


async def test_request_429_raises_tractive_error(auth_response):
    """
    Rate limiting (429) currently raises TractiveError instead of retrying.
    The retry logic doesn't work because raise_for_status=True throws before
    we can check the status code.
    """
    with aioresponses() as m:
        mock_auth(m, auth_response)
        m.get(f"{API_URL}/tracker/test123", status=429)

        async with Tractive("test@example.com", "password") as client:
            with pytest.raises(TractiveError):
                await client.tracker("test123").details()


async def test_user_id(auth_response):
    with aioresponses() as m:
        mock_auth(m, auth_response)

        async with Tractive("test@example.com", "password") as client:
            assert await client._api.user_id() == "test_user_123"


async def test_auth_headers(auth_response):
    with aioresponses() as m:
        mock_auth(m, auth_response)

        async with Tractive("test@example.com", "password") as client:
            headers = await client._api.auth_headers()

            assert headers["authorization"] == "Bearer test_access_token_xyz"
            assert headers["x-tractive-user"] == "test_user_123"
