"""
This example set demonstrates the use of the enforce_defined function.
The enforce_defined function can be used to assert that a value is
defined (not None).
"""

from __future__ import annotations

from buzz import enforce_defined

from helpers import wrap_demo


def simple_enforce_defined():
    """
    This function demonstrates the simplest use of the enforce_defined
    function. This function can be used any time a a value needs to be checked
    to ensure it is defined. This function is best used in an assignment
    expression so that static type checker's won't complain if you attempt to
    access an attribute of a value that may not be undefined.
    """
    val: str | None = "test-value"
    val = enforce_defined(val)
    # I can safely access the `upper()` method of `val` now."
    val.upper()

    enforce_defined(None)


class DemoException(Exception):
    def __init__(self, message, demo_arg, demo_kwarg=None):
        super().__init__(message)
        self.demo_arg = demo_arg
        self.demo_kwarg = demo_kwarg

    def __str__(self):
        return f"{super().__str__()} (with demo_arg={self.demo_arg} and demo_kwarg={self.demo_kwarg})"


def get_val(defined=True) -> str | None:
    if defined:
        return "test-value"
    else:
        return None


def complex_enforce_defined():
    """
    This function demonstrates a more complex usage of the enforce_defined
    function. It shows the ability to supply a custom message, raise specific
    exception types, and pass args and kwargs to the raised exception.
    """
    val = enforce_defined(get_val(defined=True), "This condition should pass")
    val.upper()

    val = enforce_defined(
        get_val(defined=False),
        f'Value is not defined!!!',
        raise_exc_class=DemoException,
        raise_args=["foo"],
        raise_kwargs=dict(demo_kwarg="bar"),
    )
    val.upper()


if __name__ == '__main__':
    with wrap_demo("Demonstrating simple enforce_defined example"):
        simple_enforce_defined()

    with wrap_demo("Demonstrating complex enforce_defined example"):
        complex_enforce_defined()
