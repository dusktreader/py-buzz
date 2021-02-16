"""
This example set demonstrates the use of the check_expressions context manager.
This context manager is intended to be a tool that can check many conditions
and provide a report of which failed inside of a single exception. If all the
conditions pass, no exception is raised
"""

from math import sqrt

from buzz import Buzz


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
    with Buzz.check_expressions("Some checks failed for {}".format(n)) as check:
        check(is_int(n), "number must be even")
        check(is_power_of_2(n), "number must be a power of 2")
        check(is_prime(n), "number must be prime")


def complex_check_expressions():
    """
    This function demonstrates usage of the check_expressions context manager.
    """
    print("Demonstrating complex check_expressions example")

    for n in (2, 4, 6, 7.5):
        try:
            print("Checking {}".format(n))
            check_number(n)
        except Buzz as err:
            print(err)


if __name__ == "__main__":
    complex_check_expressions()
