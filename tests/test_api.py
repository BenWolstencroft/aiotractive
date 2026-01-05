"""Tests for the API client."""

from __future__ import annotations

from typing import Any

import pytest
from aioresponses import aioresponses

from aiotractive import Tractive
from aiotractive.api import API
from aiotractive.exceptions import NotFoundError, TractiveError, UnauthorizedError

API_URL = str(API.API_URL)


def mock_auth(mock: aioresponses, auth_response: dict[str, Any]) -> None:
    """Add authentication endpoint mock to aioresponses."""
    mock.post(f"{API_URL}auth/token", payload=auth_response)


async def test_auth_success(auth_response: dict[str, Any]) -> None:
    """Test successful authentication returns user_id and access_token."""
    with aioresponses() as mock:
        mock_auth(mock, auth_response)

        async with Tractive("test@example.com", "password") as client:
            creds = await client.authenticate()
            assert creds is not None

            assert creds["user_id"] == "test_user_123"
            assert creds["access_token"] == "test_access_token_xyz"  # noqa: S105


async def test_auth_caches_credentials(auth_response: dict[str, Any]) -> None:
    """Test that credentials are cached and not re-fetched on subsequent calls."""
    with aioresponses() as mock:
        mock_auth(mock, auth_response)

        async with Tractive("test@example.com", "password") as client:
            creds1 = await client.authenticate()
            creds2 = await client.authenticate()
            assert creds1 is creds2  # Same object, not a new request


@pytest.mark.parametrize("status", [401, 403])
async def test_auth_invalid_credentials(status: int) -> None:
    """Test that 401 and 403 responses raise UnauthorizedError."""
    with aioresponses() as mock:
        mock.post(f"{API_URL}auth/token", status=status)

        async with Tractive("test@example.com", "wrong") as client:
            with pytest.raises(UnauthorizedError):
                await client.authenticate()


async def test_request_404_raises_not_found(auth_response: dict[str, Any]) -> None:
    """Test that 404 response raises NotFoundError."""
    with aioresponses() as mock:
        mock_auth(mock, auth_response)
        mock.get(f"{API_URL}tracker/bad_id", status=404)

        async with Tractive("test@example.com", "password") as client:
            with pytest.raises(NotFoundError):
                await client.tracker("bad_id").details()


async def test_request_500_raises_tractive_error(auth_response: dict[str, Any]) -> None:
    """Test that 500 server error raises TractiveError."""
    with aioresponses() as mock:
        mock_auth(mock, auth_response)
        mock.get(f"{API_URL}tracker/test123", status=500)

        async with Tractive("test@example.com", "password") as client:
            with pytest.raises(TractiveError):
                await client.tracker("test123").details()


async def test_request_429_raises_tractive_error(auth_response: dict[str, Any]) -> None:
    """Rate limiting (429) currently raises TractiveError instead of retrying.

    The retry logic doesn't work because raise_for_status=True throws before
    we can check the status code.
    """
    with aioresponses() as mock:
        mock_auth(mock, auth_response)
        mock.get(f"{API_URL}tracker/test123", status=429)

        async with Tractive("test@example.com", "password") as client:
            with pytest.raises(TractiveError):
                await client.tracker("test123").details()


async def test_user_id(auth_response: dict[str, Any]) -> None:
    """Test that user_id() returns the authenticated user's ID."""
    with aioresponses() as mock:
        mock_auth(mock, auth_response)

        async with Tractive("test@example.com", "password") as client:
            assert await client._api.user_id() == "test_user_123"


async def test_auth_headers(auth_response: dict[str, Any]) -> None:
    """Test that auth_headers() returns correct authorization and user headers."""
    with aioresponses() as mock:
        mock_auth(mock, auth_response)

        async with Tractive("test@example.com", "password") as client:
            headers = await client._api.auth_headers()

            assert headers["authorization"] == "Bearer test_access_token_xyz"
            assert headers["x-tractive-user"] == "test_user_123"
