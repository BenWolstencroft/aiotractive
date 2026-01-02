"""Entrypoint for the Tractive REST API."""

from collections.abc import AsyncIterator
from types import TracebackType
from typing import Any, cast

from .api import API
from .channel import Channel
from .trackable_object import TrackableObject
from .tracker import Tracker


class Tractive:
    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        """Initialize the client."""
        self._api = API(*args, **kwargs)

    async def authenticate(self) -> dict[str, Any] | None:
        return await self._api.authenticate()

    async def trackers(self) -> list[Tracker]:
        trackers = cast(
            "list[dict[str, Any]]",
            await self._api.request(f"user/{await self._api.user_id()}/trackers"),
        )
        return [Tracker(self._api, t) for t in trackers]

    def tracker(self, tracker_id: str) -> Tracker:
        return Tracker(self._api, {"_id": tracker_id, "_type": "tracker"})

    def trackable_object(self, trackable_id: str) -> TrackableObject:
        return TrackableObject(self._api, {"_id": trackable_id, "_type": "pet"})

    async def trackable_objects(self) -> list[TrackableObject]:
        objects = cast(
            "list[dict[str, Any]]",
            await self._api.request(
                f"user/{await self._api.user_id()}/trackable_objects",
            ),
        )
        return [TrackableObject(self._api, t) for t in objects]

    async def events(self) -> AsyncIterator[dict[str, Any]]:
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
