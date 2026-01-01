"""Entrypoint for the Tractive REST API."""

from collections.abc import AsyncIterator
from types import TracebackType
from typing import Any

from .api import API
from .channel import Channel
from .trackable_object import TrackableObject
from .tracker import Tracker


class Tractive:
    """Main entrypoint for the Tractive API client.

    Use as an async context manager for automatic session cleanup:

        async with Tractive("email", "password") as client:
            trackers = await client.trackers()
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the client.

        Args:
            *args: Passed to API (login, password).
            **kwargs: Passed to API (client_id, timeout, session, etc.).

        """
        self._api = API(*args, **kwargs)

    async def authenticate(self) -> dict[str, Any] | None:
        """Authenticate with the Tractive API.

        Returns:
            User credentials including user_id, access_token, and expires_at.

        """
        return await self._api.authenticate()

    async def trackers(self) -> list[Tracker]:
        """Get all trackers for the authenticated user.

        Returns:
            List of Tracker objects.

        """
        trackers = await self._api.request(f"user/{await self._api.user_id()}/trackers")
        return [Tracker(self._api, t) for t in trackers]

    def tracker(self, tracker_id: str) -> Tracker:
        """Get a tracker by ID without fetching details.

        Args:
            tracker_id: The tracker's unique ID.

        Returns:
            Tracker object (call methods like details() to fetch data).

        """
        return Tracker(self._api, {"_id": tracker_id, "_type": "tracker"})

    def trackable_object(self, trackable_id: str) -> TrackableObject:
        """Get a trackable object by ID without fetching details.

        Args:
            trackable_id: The trackable object's unique ID.

        Returns:
            TrackableObject (call methods like details() to fetch data).

        """
        return TrackableObject(self._api, {"_id": trackable_id, "_type": "pet"})

    async def trackable_objects(self) -> list[TrackableObject]:
        """Get all trackable objects (pets) for the authenticated user.

        Returns:
            List of TrackableObject instances.

        """
        objects = await self._api.request(
            f"user/{await self._api.user_id()}/trackable_objects",
        )
        return [TrackableObject(self._api, t) for t in objects]

    async def events(self) -> AsyncIterator[dict[str, Any]]:
        """Subscribe to real-time events from Tractive.

        Yields:
            Event dictionaries from the Tractive channel.

        """
        async for event in Channel(self._api).listen():
            yield event

    async def close(self) -> None:
        """Close open client session."""
        await self._api.close()

    async def __aenter__(self) -> "Tractive":
        """Async enter."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Async exit."""
        await self.close()
