"""
This demo shows how to raise a new exception from an existing exception with `raise_from()`.
"""

from __future__ import annotations

from buzz import Buzz, raise_from


def demo_1__preserve_cause():
    """
    This function demonstrates how the `raise_from()` function raises a new exception of the
    provided type from an existing exception while reformatting the final message to wrap the
    original exception message.
    """
    try:
        raise OSError("connection refused")
    except OSError as err:
        raise_from("Could not load the profile", err, raise_exc_class=RuntimeError)


def demo_2__buzz_class():
    """
    This function demonstrates how the `raise_from()` method on a Buzz-derived class raises a
    new exception of the provided type from an existing exception while reformatting the final
    message to wrap the original exception message.
    """

    class ProfileError(Buzz):
        pass

    try:
        raise OSError("connection refused")
    except OSError as err:
        ProfileError.raise_from("Could not load the profile", err)
