"""
This example set demonstrates the use of the require_conditions function.
The require_condtion function can be used to assert a boolean condition
wherever needed.
"""

from buzz import Buzz
from sys import argv


def is_even(i):
    return i % 2 == 0


def simple_require_condition():
    """
    This function demonstrates the simplest use of the require_condition
    function. This function can be used any time a state invariant needs to be
    asserted. Unlike the built-in assert keyword, require_condition will be
    in effect in both live and debug modes.
    """
    print("Demonstrating simple require_condition example")
    Buzz.require_condition(True, 'This condition should always pass')
    Buzz.require_condition(False, 'This condition should always fail')


def complex_require_condition():
    """
    This function demonstrates a more complex usage of the require_condition
    function. It shows argument interpolation and handling a more complex
    boolean expression
    """
    print("Demonstrating complex require_condition example")

    val = 64
    Buzz.require_condition(is_even(val), 'This condition should pass')
    val = 81
    Buzz.require_condition(is_even(val), 'Value {val} is not even', val=val)


if __name__ == '__main__':
    if len(argv) == 1 or argv[1] == 'simple':
        simple_require_condition()
    elif argv[1] == 'complex':
        complex_require_condition()
    else:
        print("No example selected. Call with one arg: 'simple' or 'complex'")
