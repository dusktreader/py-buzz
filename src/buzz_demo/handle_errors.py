"""
This set of demos shows the use of the `handle_errors()` context manager.

The `handle_errors()` context manager effectively wraps a block of code with
a try-except without having to explicitly declare them. Additionally, it wraps
all caught exceptions from the block in custom error messages that include
the original error text as well as a user supplied message.
"""
from __future__ import annotations

from typing import Any

from buzz import handle_errors, DoExceptParams


def demo_1__simple():
    """
    This function demonstrates the simplest use of the `handle_errors()` context
    manager. Note how the nested exception type is ValueError. The error
    produced by the handle_errors context manager will be of type `Exception`
    (because no `raise_exc_class` argument was supplied. The resulting exception
    message will include the message supplied to the handle_error context
    manager as well as the message of the nested exception
    """
    with handle_errors("something went wrong (simple example)"):
        print("here we are fine")
        raise ValueError("here we die")
    print("we should not get here")  # pyright: ignore[reportUnreachable]


def demo_2__absorbing():
    """
    This function demonstrates a more complex usage of the `handle_errors()`
    context manager where exceptions are absorbed. When the `raise_exc_class`
    parameter is set to None, the `handle_errors()` context manager will
    effectively swallow any exceptions that it handles. The following features
    are demonstrated:

    * Handling a specific exception type with `exception_class`
    * Absorbing exceptions by setting `raise_exc_class` to `None`
    * Branching with `do_except`, `do_else`, and `do_finally`
    """
    def _handler_function(dep: DoExceptParams):
        print("do_except() was called!")
        print(f"Handling exception: {dep.err}")
        print(f"Final Message: {dep.final_message}")

    with handle_errors(
        "something went wrong (complex example)",
        raise_exc_class=None,
        do_except=_handler_function,
        do_else=lambda: print('do_else() was called!'),
        do_finally=lambda: print('do_finally() was called!'),
    ):
        print("here we are fine")
        raise ValueError("here we die")
        print("we should not get here")  # pyright: ignore[reportUnreachable]


def demo_3__multiple():
    """
    This function demonstrates handling more than one exception type with the
    `handle_errors()` context manager. The `handle_exc_class` parameter can be
    used to provide a single exception class (including its descendants) that
    should be handled. It can also provide an iterable of exception classes
    (and their descendants) that should be handled. The following features are
    demonstrated:

    * Handling multiple exception types

    Note that the final `TypeError` is _not_ handled!
    """
    def _handler_function(dep: DoExceptParams):
        """
        This function is a helper function for handling an exception from
        the handle_errors context manager.
        """
        print(f"Handling exception type {dep.err.__class__}: {dep.final_message}")

    for exception_class in (ValueError, RuntimeError, AttributeError, TypeError):
        with handle_errors(
            "something went wrong (multiple example)",
            handle_exc_class=(ValueError, RuntimeError, AttributeError),
            do_except=_handler_function,
            raise_exc_class=None,
        ):
            print(f"trying out {exception_class}")
            print("here we are fine")
            raise exception_class("here we die")
            print("we should not get here")  # pyright: ignore[reportUnreachable]
        print("we will only get here if the exception was handled")  # pyright: ignore[reportUnreachable]



def demo_4__specific():
    """
    This function demonstrates how the `handle_errors()` context manager can be
    used to raise a specific exception type that wraps the error message of the
    handled exception. The following features are demonstrated:

    * Raising a specific exception instance using the `raise_exc_class` parameter
    * Passing along `raise_args` and `raise_kwargs` when raising the exception
    """
    class DerivedError(Exception):
        def __init__(self, message: str, init_arg: Any, init_kwarg: Any | None = None):
            self.init_arg: Any = init_arg
            self.init_kwarg: Any = init_kwarg
            super().__init__(message)
            print(f"with: init_arg='{self.init_arg}', init_kwarg='{self.init_kwarg}'")

    with handle_errors(
        "something went wrong (specific example)",
        raise_exc_class=DerivedError,
        raise_args=["init arg"],
        raise_kwargs=dict(init_kwarg="init kwarg"),
    ):
        print("here we are fine")
        raise ValueError("here we die")
        print("we should not get here")  # pyright: ignore[reportUnreachable]


def demo_5__ignoring():
    """
    This function demonstrates how specific exception classes can be ignored by the
    `handle_errors()` context manager even if they derive from the exception class
    provided with `handle_exc_class`. In this demo, any of the handled (and not ignored)
    exception classes will be absorbed because the `raise_exc_class` parameter is set to
    `None`. The following features are demonstrated:

    * Ignoring specific exception types
    """
    for exception_class in (ValueError, RuntimeError):
        with handle_errors(
            "something went wrong (ignore example)",
            handle_exc_class=Exception,
            ignore_exc_class=RuntimeError,
            raise_exc_class=None,
        ):
            print(f"trying out {exception_class}")
            print("here we are fine")
            raise exception_class("here we die")
            print("we should not get here")  # pyright: ignore[reportUnreachable]
        print("we will only get here if the exception was not ignored")  # pyright: ignore[reportUnreachable]
