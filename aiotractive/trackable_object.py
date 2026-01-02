"""Representation of a Tractive trackable object (pet)."""

from typing import Any, cast

from .data_object import DataObject


class TrackableObject(DataObject):
    """Representation of a Tractive trackable object (pet)."""

    async def details(self) -> dict[str, Any]:
        """Get trackable object details."""
        return cast(
            "dict[str, Any]", await self._api.request(f"trackable_object/{self._id}")
        )

    async def health_overview(self) -> dict[str, Any]:
        """Get health overview data including activity, sleep, rest, and health metrics.

        Returns health_overview data from the APS API endpoint.
        Replaces the deprecated wellness_overview message.
        """
        return cast(
            "dict[str, Any]",
            await self._api.request(
                f"pet/{self._id}/health/overview",
                base_url=self._api.APS_API_URL,
            ),
        )
