"""
This set of demos show how to use `verify_literal()`.

The `verify_literal()` function is useful for checking that a value is one of
the allowed values of a `typing.Literal` type. If the value does not match, an
exception will be raised. Otherwise, the value will be returned unchanged.

This is especially useful when you have a variable that could be any `str` (or
`int`, `bytes`, etc.) but you need to guarantee it is one of a fixed set of
known values before proceeding. Note that full type narrowing to the specific
`Literal` type is not currently possible without `TypeForm` support in the type
system — the return type reflects the input value's declared type.
"""

from __future__ import annotations

from typing import Any, Literal

from typing_extensions import override

from buzz import verify_literal


def demo_1__simple():
    """
    This function demonstrates the simplest use of the `verify_literal()`
    function. The value `"foo"` is a member of `Literal["foo", "bar", "baz"]`,
    so it passes and is returned unchanged.
    """
    val = "foo"
    val = verify_literal(val, Literal["foo", "bar", "baz"], "This will pass!")
    print(f"verify_literal() returned: {val!r}")


def demo_2__failing():
    """
    This function demonstrates what happens when the `verify_literal()` function
    raises an exception because the value is not one of the allowed literals.
    """
    val = "qux"
    val = verify_literal(val, Literal["foo", "bar", "baz"], "This will not pass!")
    print("I should not be able to get to this line.")


def demo_3__complex():
    """
    This function demonstrates a more complex usage of `verify_literal()`.
    The following features are demonstrated:

    * Using a custom failure message
    * Raising a specific exception type on failure
    * Passing specific args and kwargs to the exception when it is raised
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

    val = "foo"
    val = verify_literal(val, Literal["foo", "bar", "baz"], "This condition should pass")
    print(f"verify_literal() returned: {val!r}")

    val = "qux"
    val = verify_literal(
        val,
        Literal["foo", "bar", "baz"],
        "Value is not an allowed literal",
        raise_exc_class=DemoException,
        raise_args=["jawa"],
        raise_kwargs=dict(demo_kwarg="ewok"),
        do_except=lambda exc: print(f"do_except() was called: {exc}!"),
    )
    print("I should not be able to get to this line.")
