"""
This set of demos shows how to use the `Buzz` exception class.

`Buzz` is an exception class with some special features. It is very useful to
use a custom class derived from `Buzz` to use as a base exception class for a
project. In this way, you can define several custom exception types that all
include the features of `Buzz`.
"""
from __future__ import annotations

from buzz import Buzz


def demo_1__check_expressions():
    """
    This function demonstrates simple usage of the `check_expressions()` context
    manager from `Buzz`. Notice how the raised exception is an instance of `Buzz`
    without the need to set the `raise_exc_class`. In fact, `Buzz` does not allow
    you to supply a `raise_exc_class` parameter for this reason.
    """
    with Buzz.check_expressions("Some checks failed!") as check:
        check(13 > 21, "thirteen was not greater than twenty-one!")
        check(True is False, "True is not False!")  # pyright: ignore[reportUnnecessaryComparison]


def demo_2__handle_errors():
    """
    This function demonstrates basic usage of the `handle_errors()` context manager
    from `Buzz`. Notice how the raised exception is an instance of `Buzz` without
    the need to set the `raise_exc_class`.
    """
    with Buzz.handle_errors("something went wrong (simple example)"):
        print("here we are fine")
        raise ValueError("here we die")
    print("we should not get here")  # pyright: ignore[reportUnreachable]


def demo_3__enforce_defined():
    """
    This function demonstrates the basic use of the `enforce_defined()`
    function from `Buzz`. Notice how the riased exception is an instance of `Buzz`
    without the need to set the `raise_exc_class`.
    """
    val: str | None = "test-value"
    val = Buzz.enforce_defined(val)
    print("I should be able to safely access the `upper()` method of `val` now.")
    print("There should also be no type errors because `val` is now guaranteed to be a string.")
    val.upper()


def demo_4__require_condition():
    """
    This function demonstrates very basic use of the `require_condition()`
    function from `Buzz`. Notice how the raised exception is an instance of `Buzz`
    without th eneed to set the `raise_exc_class`.
    """
    Buzz.require_condition(True, 'This condition should always pass')
    print("I got past the first condition")

    Buzz.require_condition(False, 'This condition should always fail')
    print("I won't get past the second condition")


def demo_5__derived_classes():
    """
    This function demonstrates how derived classes from Buzz can be used. In this
    case, `EwokError` is going to be ignored and all other exceptions that derive
    from `Buzz` will be handled. Non-`Buzz` exceptions will not be handled either
    because the `handle_exc_class` parameter is set to `Buzz`.
    The following features are demonstrated:

    * Using derived classes
    * Ignoring specific derived classes
    * Only handling `Buzz` classes
    * Not handling non-`Buzz` errors
    * Absorbing exceptions by setting the `re_raise` flag
    """
    class JawaError(Buzz):
        pass

    class EwokError(Buzz):
        pass

    for exception_class in (JawaError, EwokError, Buzz, RuntimeError):
        try:
            with Buzz.handle_errors(
                "something went wrong (derived example)",
                handle_exc_class=Buzz,
                ignore_exc_class=EwokError,
                re_raise=False
            ):
                print(f"trying out {exception_class}")
                print("here we are fine")
                raise exception_class("here we die")
                print("we should not get here")  # pyright: ignore[reportUnreachable]
        except Exception:
            print("we should only get here for unhandled and ignored errors")
