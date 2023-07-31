"""
This example demonstrates how to use the exc_builder option to use a
builder function to construct exceptions with non-standard signatures.
This is needed, for example, with FastAPI's HTTPException where the
first positional argument is not a message but a status_code.
"""
from buzz import handle_errors

from helpers import wrap_demo


class WeirdArgsException(Exception):
    def __init__(self, demo_arg, demo_kwarg=None, detail=""):
        self.demo_arg = demo_arg
        self.demo_kwarg = demo_kwarg
        self.detail = detail

    def __str__(self):
        return (
            f"{self.__class__.__name__} (with demo_arg={self.demo_arg}, demo_kwarg={self.demo_kwarg}, "
            f"and detail={self.detail})"
        )


def weird_args_builder(exc_class, message, *args, **kwargs):
    return exc_class(*args, detail=message, **kwargs)


def use_exc_builder():
    """
    This function demonstrates how the exc_builder keyword argument can
    be used to provide an alternative exception builder for exception
    classes that use non-standard args and kwargs.

    An real-world example of this is FastAPI's HTTPException which has
    status_code as the first positional argument instead of a message.
    """
    with handle_errors(
        "something went wrong (using exc_builder)",
        raise_exc_class=WeirdArgsException,
        raise_args=["foo"],
        raise_kwargs=dict(demo_kwarg="bar"),
        exc_builder=weird_args_builder,
    ):
        print("we are fine")
        raise RuntimeError("here we die")
    print("we should not get here")  # type: ignore[unreachable]


if __name__ == '__main__':
    with wrap_demo("Demonstrating use of exc_builder option"):
        use_exc_builder()()
