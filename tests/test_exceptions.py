"""Tests for exception classes."""

import pytest

from aiotractive.exceptions import DisconnectedError, NotFoundError, TractiveError, UnauthorizedError


@pytest.mark.parametrize("exc_class", [UnauthorizedError, NotFoundError, DisconnectedError])
def test_subclasses_inherit_from_tractive_error(exc_class):
    assert issubclass(exc_class, TractiveError)
    assert issubclass(TractiveError, Exception)


def test_can_catch_specific_exception():
    with pytest.raises(UnauthorizedError):
        raise UnauthorizedError("Invalid credentials")


def test_can_catch_as_base_exception():
    # All specific exceptions should be catchable as TractiveError
    for exc in [UnauthorizedError("test"), NotFoundError("test"), DisconnectedError("test")]:
        with pytest.raises(TractiveError):
            raise exc


def test_exception_message_preserved():
    msg = "Something went wrong"
    err = TractiveError(msg)
    assert str(err) == msg
