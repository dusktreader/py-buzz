"""
This set of demos show how to use `ensure_type()`.

The `ensure_type()` function is useful for checking that a value
matches a specific type. If the value does not match, an
exception will be raised. Otherwise, the value will be returned _and_
cast to the type it was checked against.

This is especially useful for variables that can be initialized as more
than one type, but you need to access an attribute of them that only
exists in _one_ of the types that they may be. Typically, type checkers
will give you a hard time unless you explicitly cast the variable to a
that specific type or add an assertion of `isinstance()`. This can be an
annoying pattern to have to repeat all over the place. The `ensure_type()`
function an be used practically to guarantee that the variable is of the
and narrow its type.
"""
from __future__ import annotations

from typing import Any
from typing_extensions import override

from buzz import ensure_type


def demo_1__simple():
    """
    This function demonstrates the simplest use of the `ensure_type()`
    function. This function can be used any time a a value needs to be checked
    to ensure it is of a specific type. This function is best used in an
    assignment expression so that static type checkers won't complain if you
    attempt to access an attribute of a value that may be of many types and the
    attribute only exists on one of them.
    """
    val: str | int = "test-value"
    val = ensure_type(val, str)
    print("I should be able to safely access the `upper()` method of `val` now.")
    print("There should also be no type errors because `val` is now guaranteed to be a string.")
    val.upper()


def demo_2__failing():
    """
    This function demonstrates what happens when the `ensure_type()` function
    raises an exception due to the value being of the wrong type.
    """
    val: str | int = 13
    val = ensure_type(val, str)
    print("I should not be able to get to this line because `ensure_type()` should fail.")
    val.upper()


def demo_3__complex():
    """
    This function demonstrates a more complex usage of the `ensure_type()`
    function. It will raise a specific exception type on failure with some
    custom values bound to the exception instance. The following features are
    demonstrated:

    * Using a custom failure message
    * Raising a specific exception types on failure
    * Passing specific args and kwargs to the exception when it is raised.
    * Calling a `do_except()` function
    """
    class DemoException(Exception):
        def __init__(self, message: str, demo_arg: Any, demo_kwarg: Any | None = None):
            super().__init__(message)
            self.demo_arg: Any = demo_arg
            self.demo_kwarg: Any = demo_kwarg

        @override
        def __str__(self):
            return f"{super().__str__()} (with demo_arg={self.demo_arg} and demo_kwarg={self.demo_kwarg})"

    val: str | int = "dummy"
    val = ensure_type(val, str, "This condition should pass")
    val.upper()
    val = 13
    val = ensure_type(
        val,
        str,
        "Value is not a string",
        raise_exc_class=DemoException,
        raise_args=["jawa"],
        raise_kwargs=dict(demo_kwarg="ewok"),
        do_except=lambda exc: print(f"do_except() was called: {exc}!"),
    )
    val.upper()
