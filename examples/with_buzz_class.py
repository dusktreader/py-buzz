"""
This example shows how the Buzz exception class might be used as the base of a derived class
"""
from buzz import Buzz

from helpers import wrap_demo



class DerivedError(Buzz):
    pass


def demo_check_expression():
    with DerivedError.check_expressions(f"Some of our expressions were falsey!") as check:
        check(False, "False is always False")
        check(0, "Zero is the only falsey integer")
        check("", "Empty strings are also falsey!")


def demo_handle_errors():
    with DerivedError.handle_errors("something went wrong (simple example)"):
        print("we are fine")
        raise ValueError("here we die")
        print("we should not get here")


def demo_require_conditions():
    DerivedError.require_condition(True, 'This condition should always pass')
    DerivedError.require_condition(False, 'This condition should always fail')


if __name__ == '__main__':
    with wrap_demo("Demonstrating check_expressions from Buzz derived class"):
        demo_check_expression()

    with wrap_demo("Demonstrating handle_errors from Buzz derived class"):
        demo_handle_errors()

    with wrap_demo("Demonstrating require_conditions from Buzz derived class"):
        demo_handle_errors()
