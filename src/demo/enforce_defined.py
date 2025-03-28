"""
This set of demos show how to use `enforce_defined()`.

The `enforce_defined()` function is useful for checking a value
that may be `None` or some non-null value. If the value is `None`, an
exception will be raised. Otherwise, a "non-null" version of the value
is returned.

This is especially useful for variables that are nullable, but you need
to access an attribute of them (when they are not `None`). Typically,
type checkers will give you a hard time unless you explicitly cast the
variable to a non-null type or add an assertion that the value is not
`None`. Neither of these look particularly good. However, this check can
be used practically to guarantee that the variable is set and narrow its
type.
"""
from __future__ import annotations

from typing import Any
from typing_extensions import override

from buzz import enforce_defined


def demo_1__simple():
    """
    This function demonstrates the simplest use of the `enforce_defined()`
    function. This function can be used any time a a value needs to be checked
    to ensure it is defined. This function is best used in an assignment
    expression so that static type checkers won't complain if you attempt to
    access an attribute of a value that may not be undefined.
    """
    val: str | None = "test-value"
    val = enforce_defined(val)
    print("I should be able to safely access the `upper()` method of `val` now.")
    print("There should also be no type errors because `val` is now guaranteed to be a string.")
    val.upper()

def demo_2__failing():
    """
    This function demonstrates what happens when the `enforce_defined()`
    function raises an exception due to the value being `None`.
    """
    val: str | None = None
    val = enforce_defined(val)
    print("I should not be able to get to this line because `enforce_defined()` should fail.")
    val.upper()


def demo_3__complex():
    """
    This function demonstrates a more complex usage of the enforce_defined
    function. It will raise a specific exception type on failure with some
    custom values bound to the exception instance. The following features are
    demonstrated:

    * Using a custom failure message
    * Raising a specific exception types on failure
    * Passing specific args and kwargs to the exception when it is raised.
    """
    class DemoException(Exception):
        def __init__(self, message: str, demo_arg: Any, demo_kwarg: Any | None = None):
            super().__init__(message)
            self.demo_arg: Any = demo_arg
            self.demo_kwarg: Any = demo_kwarg

        @override
        def __str__(self):
            return f"{super().__str__()} (with demo_arg={self.demo_arg} and demo_kwarg={self.demo_kwarg})"

    def get_val(defined: bool = True) -> str | None:
        if defined:
            return "test-value"
        else:
            return None

    val = enforce_defined(get_val(defined=True), "This condition should pass")
    val.upper()
    val = enforce_defined(
        get_val(defined=False),
        "Value is not defined",
        raise_exc_class=DemoException,
        raise_args=["jawa"],
        raise_kwargs=dict(demo_kwarg="ewok"),
    )
    val.upper()
