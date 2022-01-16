"""
This example set demonstrates the use of the require_conditions function.
The require_condtion function can be used to assert a boolean condition
wherever needed.
"""
from buzz import require_condition

from helpers import wrap_demo


def simple_require_condition():
    """
    This function demonstrates the simplest use of the require_condition
    function. This function can be used any time a state invariant needs to be
    asserted. Unlike the built-in assert keyword, require_condition will be
    in effect in both live and debug modes.
    """
    require_condition(True, 'This condition should always pass')
    require_condition(False, 'This condition should always fail')


class DemoException(Exception):
    def __init__(self, message, demo_arg, demo_kwarg=None):
        super().__init__(message)
        self.demo_arg = demo_arg
        self.demo_kwarg = demo_kwarg

    def __str__(self):
        return f"{super().__str__()} (with demo_arg={self.demo_arg} and demo_kwarg={self.demo_kwarg})"


def is_even(i):
    return i % 2 == 0


def complex_require_condition():
    """
    This function demonstrates a more complex usage of the require_condition
    function. It shows the ability to raise sepcific exception types,
    handling a more complex boolean expression, and passing args and kwargs
    to the raised exception
    """
    val = 64
    require_condition(is_even(val), 'This condition should pass')
    val = 81
    require_condition(
        is_even(val),
        f'Value {val} is not even',
        raise_exc_class=DemoException,
        raise_args=["foo"],
        raise_kwargs=dict(demo_kwarg="bar"),
    )


if __name__ == '__main__':
    with wrap_demo("Demonstrating simple require_condition example"):
        simple_require_condition()

    with wrap_demo("Demonstrating complex require_condition example"):
        complex_require_condition()
