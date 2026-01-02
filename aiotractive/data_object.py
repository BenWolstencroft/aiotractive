from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .api import API


class DataObject:
    def __init__(self, api: API, data: dict[str, Any]) -> None:
        self._api = api
        self._id: str = data["_id"]
        self.type: str = data["_type"]

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self._id} type={self.type}>"
