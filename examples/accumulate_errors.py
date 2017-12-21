"""
This example set demonstrates the use of the accumulate context manager.
This context manager is intended to be a tool that can check many conditions
and provide a report of which failed inside of a single exception. If all the
conditions pass, no exception is raised
"""

from buzz import Buzz
from math import sqrt


def is_int(i):
    return int(i) == i


def is_even(i):
    return i % 2 == 0


def is_power_of_2(i):
    if not is_int(i):
        return False
    i = int(i)
    return ((i & (i - 1)) == 0) and i != 0


def is_prime(i):
    if not is_int(i):
        return False
    if i % 2 == 0 and i > 2:
        return False
    return all(i % n for n in range(3, int(sqrt(i)) + 1, 2))


def check_number(n):
    with Buzz.accumulate_errors("Some checks failed for {}", n) as acc:
        acc += is_int(n)
        acc += is_even(n)
        acc += is_power_of_2(n)
        acc += is_prime(n)


def complex_accumulate_errors():
    """
    This function demonstrates usage of the accumulate_errors context manager.

    This mechanism is used to accumulate failures of boolean evaluated
    expressions. It is a fairly specialized tool that may be hard to find
    specific usses for
    """
    print("Demonstrating complex accumuilate_errors example")

    check_number(2)
    check_number(7.5)


if __name__ == '__main__':
    complex_accumulate_errors()
