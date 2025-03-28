"""
This set of demos shows the use of the check_expressions context manager.

This context manager is intended to be a tool that can check many conditions
and provide a report of which failed inside of a single exception. If all the
conditions pass, no exception is raised.
"""
from __future__ import annotations

from buzz import check_expressions


def demo_1__simple():
    """
    This function demonstrates simple usage of the check_expression context manager.
    It will check two conditions to make sure that both are truthy. If any fail,
    an exception will be raised.
    """
    with check_expressions("Some checks failed!") as check:
        check(13 > 21, "thirteen was not greater than twenty-one!")
        check(True is False, "True is not False!")  # pyright: ignore[reportUnnecessaryComparison]


def demo_2__complex():
    """
    This function demonstrates complex usage of the check_expression context manager.
    It will check whether an input value meets several criteria. If any of the criteria
    fail, an exception will be raised. The following features are demonstrated:

    * Applying multiple checks
    * Applying all checks provided, even if one fails early in the process.
    * Raising a specific exception type on failure
    """
    def is_int(n: float | int):
        return int(n) == n

    def is_positive(n: float | int):
        return n > 0.0

    def is_even(n: float | int):
        return is_int(n) and n % 2 == 0

    def is_power_of_2(n: float | int):
        return is_int(n) and ((int(n) & (int(n) - 1)) == 0) and n != 0

    def is_prime(n: float | int):
        return is_int(n) and is_positive(n) and n > 1 and all(n % i for i in range(2, int(n**0.5) + 1))

    n = 8
    with check_expressions(f"Some checks failed for {n}", raise_exc_class=RuntimeError) as check:
        check(is_int(n), "number must an integer")
        check(is_even(n), "number must be even")
        check(is_power_of_2(n), "number must be a power of 2")
        check(is_prime(n), "number must be prime")
