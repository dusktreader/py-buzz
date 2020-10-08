from buzz import Buzz

"""
This example shows the most basic usage of the Buzz exception type
"""


class BasicException(Buzz):
    pass


if __name__ == "__main__":
    raise BasicException(
        "Something went wrong: {some_arg}".format(
            some_arg="interpolated-arg",
        )
    )
