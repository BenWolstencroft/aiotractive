"""Tracker data object for Tractive devices."""

from typing import Any, ClassVar, cast

from .data_object import DataObject


class Tracker(DataObject):
    """Represents a Tractive GPS tracker device."""

    ACTIONS: ClassVar[dict[bool, str]] = {True: "on", False: "off"}

    async def details(self) -> dict[str, Any]:
        """Get tracker details including capabilities, battery status, and charging state."""
        return cast("dict[str, Any]", await self._api.request(f"tracker/{self._id}"))

    async def hw_info(self) -> dict[str, Any]:
        """Get hardware info including battery level, firmware version, and model."""
        return cast(
            "dict[str, Any]", await self._api.request(f"device_hw_report/{self._id}/")
        )

    async def pos_report(self) -> dict[str, Any]:
        """Get current position report including coordinates, latitude, and speed."""
        return cast(
            "dict[str, Any]",
            await self._api.request(f"device_pos_report/{self._id}"),
        )

    async def positions(
        self, time_from: float, time_to: float, fmt: str
    ) -> dict[str, Any]:
        """Get historical positions within a time range.

        Args:
            time_from: Start timestamp (Unix epoch).
            time_to: End timestamp (Unix epoch).
            fmt: Response format (e.g., 'json_segments').

        Returns:
            Position history data.

        """
        url = f"tracker/{self._id}/positions"
        params = {
            "time_from": time_from,
            "time_to": time_to,
            "format": fmt,
        }
        return cast("dict[str, Any]", await self._api.request(url, params=params))

    async def set_buzzer_active(self, active: bool) -> dict[str, Any]:
        """Control the tracker buzzer.

        Args:
            active: True to turn on, False to turn off.

        """
        action = self.ACTIONS[active]
        return cast(
            "dict[str, Any]",
            await self._api.request(
                f"tracker/{self._id}/command/buzzer_control/{action}",
            ),
        )

    async def set_led_active(self, active: bool) -> dict[str, Any]:
        """Control the tracker LED.

        Args:
            active: True to turn on, False to turn off.

        """
        action = self.ACTIONS[active]
        return cast(
            "dict[str, Any]",
            await self._api.request(
                f"tracker/{self._id}/command/led_control/{action}",
            ),
        )

    async def set_live_tracking_active(self, active: bool) -> dict[str, Any]:
        """Control live tracking mode.

        Args:
            active: True to enable, False to disable.

        """
        action = self.ACTIONS[active]
        return cast(
            "dict[str, Any]",
            await self._api.request(
                f"tracker/{self._id}/command/live_tracking/{action}",
            ),
        )
