"""
This set of demos show how to use the `exc_builder` option.

This option provides a function that should be used to build the
instances of the exception that is raised from the `handle_errors()`
context manager. This is useful for exception classes that use
non-standard signatures. This is needed, for example, with FastAPI's
`HTTPException` where the first positional argument is not a message
but a status_code.
"""
from __future__ import annotations

from typing import Any
from typing_extensions import Self, override
from buzz import handle_errors

from buzz.base import Buzz
from buzz.tools import ExcBuilderParams


def demo_1__exc_builder():
    """
    This function demonstrates how the exc_builder keyword argument can
    be used to provide an alternative exception builder for exception
    classes that use non-standard args and kwargs. Note how the `message`
    field from the `ExcBuilderParams` is re-routed to the `detail` keyword
    argument because of the odd way that `WeirdArgsException` is
    initialized.

    An real-world example of an exception that needs modified init args is
    FastAPI's `HTTPException` which has status_code as the first positional
    argument instead of a message.
    """
    class WeirdArgsException(Exception):
        def __init__(self, demo_arg: Any, demo_kwarg: Any | None = None, detail: str = "unset detail"):
            self.demo_arg: Any = demo_arg
            self.demo_kwarg: Any = demo_kwarg
            self.detail: str = detail
            super().__init__(detail)

        @override
        def __str__(self):
            return f"with demo_arg='{self.demo_arg}', demo_kwarg='{self.demo_kwarg}', and detail='{self.detail}'"

    def weird_args_builder(params: ExcBuilderParams) -> Exception:
        return params.raise_exc_class(
            *params.raise_args,
            detail=params.message,  # pyright: ignore[reportCallIssue]
            **params.raise_kwargs,
        )  # type: ignore[call-arg]

    with handle_errors(
        "something went wrong (using exc_builder)",
        raise_exc_class=WeirdArgsException,
        raise_args=["jawa"],
        raise_kwargs=dict(demo_kwarg="ewok"),
        exc_builder=weird_args_builder,
    ):
        print("we are fine")
        raise RuntimeError("here we die")
        print("we should not get here")  # pyright: ignore[reportUnreachable]


def demo_2__buzz_class():
    """
    This function demonstrates how a customized `exc_builder` in a derived
    class of a `Buzz` exception might be used to rearrange the arguments
    that will be passed to the derived class's constructor. This example is
    somewhat contrived, but shows how a derived `Buzz` class can take
    control of how it is initialized.
    """
    class WeirdBuzz(Buzz):
        def __init__(self, *args: Any, detail: str = "unset detail", **kwargs: Any):
            self.detail: str = detail
            super().__init__(detail, *args, **kwargs)

        @override
        def __str__(self):
            return f"with detail='{self.detail}'"

        @override
        @classmethod
        def exc_builder(cls, params: ExcBuilderParams) -> Self:
            return cls(
                *params.raise_args,
                detail=params.message,
                **params.raise_kwargs,
            )

    with WeirdBuzz.handle_errors("something went wrong (using Buzz exc_builder)"):
        print("we are fine")
        raise RuntimeError("here we die")
        print("we should not get here")  # pyright: ignore[reportUnreachable]
