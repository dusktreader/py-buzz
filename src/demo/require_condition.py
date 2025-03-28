"""
This example set demonstrates the use of the `require_condition()` function.
This function can be used to assert a boolean condition wherever needed.
"""
from __future__ import annotations

from typing import Any
from typing_extensions import override
from buzz import require_condition

def demo_1__simple():
    """
    This function demonstrates very basic use of the `require_condition()`
    function. This function can be used any time a state invariant needs to be
    asserted. Unlike the built-in assert keyword, `require_condition()` will be
    in effect in both live and debug modes.
    """
    require_condition(True, 'This condition should always pass')
    print("I got past the first condition")

    require_condition(False, 'This condition should always fail')
    print("I won't get past the second condition")


def demo_2__complex():
    """
    This function demonstrates a more complex usage of the `require_condition()`
    function. It shows the ability to raise specific exception types as well
    as passing args and kwargs to the raised exception. The following features
    are demonstrated:

    * Raising a specific exception class
    * Binding extra arguments to the raised exception
    """
    class DemoException(Exception):
        def __init__(self, message: str, demo_arg: Any, demo_kwarg: Any | None = None):
            super().__init__(message)
            self.demo_arg: Any = demo_arg
            self.demo_kwarg: Any = demo_kwarg

        @override
        def __str__(self):
            return f"with demo_arg='{self.demo_arg}' and demo_kwarg='{self.demo_kwarg}'"

    require_condition(
        13 > 21,
        'Thirteen was not greater than twenty-one!',
        raise_exc_class=DemoException,
        raise_args=["jawa"],
        raise_kwargs=dict(demo_kwarg="ewok"),
    )
