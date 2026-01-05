"""Tests for exception classes."""

from __future__ import annotations

import pytest

from aiotractive.exceptions import (
    DisconnectedError,
    NotFoundError,
    TractiveError,
    UnauthorizedError,
)


@pytest.mark.parametrize(
    "exc_class", [UnauthorizedError, NotFoundError, DisconnectedError]
)
def test_subclasses_inherit_from_tractive_error(
    exc_class: type[TractiveError],
) -> None:
    """Test that all exception classes inherit from TractiveError."""
    assert issubclass(exc_class, TractiveError)
    assert issubclass(TractiveError, Exception)


def test_can_catch_specific_exception() -> None:
    """Test that specific exception types can be caught directly."""
    with pytest.raises(UnauthorizedError):
        raise UnauthorizedError("Invalid credentials")


def test_can_catch_as_base_exception() -> None:
    """Test that all specific exceptions can be caught as TractiveError."""
    for exc in [
        UnauthorizedError("test"),
        NotFoundError("test"),
        DisconnectedError("test"),
    ]:
        with pytest.raises(TractiveError):
            raise exc


def test_exception_message_preserved() -> None:
    """Test that exception message is preserved when converted to string."""
    msg = "Something went wrong"
    err = TractiveError(msg)
    assert str(err) == msg
