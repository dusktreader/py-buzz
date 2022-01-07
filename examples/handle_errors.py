"""
This example set demonstrates the use of the handle_errors context manager.
The handle_errors context manager effectively wraps a block of code with
a try-except without having to explicitly declare them. Additionally, it wraps
all caught exceptions from the block in custom error messages
"""
from traceback import format_tb

from buzz import handle_errors, DoExceptParams

from helpers import wrap_demo


def simple_handle_errors():
    """
    This function demonstrates the simplest use of the handle_errors ctx_mgr.
    Note how the nested exception type is ValueError. The error produced by
    the handle_errors ctx_mgr should be of type HandleError. The resulting
    exception message will include the message supplied to the handle_error
    ctx_mgr as well as the message of the nested exception
    """
    with handle_errors("something went wrong (simple example)"):
        print("we are fine")
        raise ValueError("here we die")
    print("we should not get here")


def absorbing_handle_errors():
    """
    This function demonstrates a more complex usage of the handle_errors
    ctx_mgr where exceptions are absorbed.
    The following features are demonstrated::

      * Handling a specific exception type with ``exception_class``
      * Absorbing exceptions by setting ``raise_exc_class`` to ``None``
      * Branching with ``do_except``, ``do_else``, and ``do_finally``
    """
    def _handler_function(dep: DoExceptParams):
        """
        This function is a helper function for handling an exception from
        the handle_errors ctx_mgr.
        """
        print("Handling exception")
        print("==================")
        print("Final Message")
        print("-------------")
        print(dep.final_message)
        print("Traceback")
        print("---------")
        print(''.join(format_tb(dep.trace)))

    with handle_errors(
            f"something went wrong (complex example)",
            raise_exc_class=None,
            do_except=_handler_function,
            do_else=lambda: print('No exception occurred'),
            do_finally=lambda: print('do_finally() was called!'),
    ):
        print("we are fine")
        raise ValueError("here we die")
        print("we should not get here")  # type: ignore[unreachable]

    print("We will get here, though, because the caught exception is not re-raised")


def multiple_handle_errors():
    """
    This function demonstrates handling more than one exception type with the
    handle_errors ctx_mgr.
    """
    def _handler_function(dep: DoExceptParams):
        """
        This function is a helper function for handling an exception from
        the handle_errors ctx_mgr.
        """
        print(f"Handling exception type {dep.err.__class__}: {dep.final_message}")

    for exception_class in (ValueError, RuntimeError, Exception):
        with handle_errors(
                f"something went wrong (multiple example)",
                raise_exc_class=None,
                do_except=_handler_function,
        ):
            print("we are fine")
            raise exception_class("here we die")
        print("we should not get here")

        print("We will not get here, because the base Exception is not handled.")


class DerivedError(Exception):

    def __init__(self, message, init_arg, init_kwarg=None):
        super().__init__(message)
        print(f"Derived Error initialized with: {init_arg=}, {init_kwarg=}")


def specific_handle_errors():
    """
    This function demonstrates how handle_errors can be used to raise a specific
    exception type that wraps the error message of the handled exception.

    The following features are demonstrated::

      * Raising a specific exception instance using the ``raise_exc_class`` parameter
      * Passing along ``raise_args`` and ``raise_kwargs`` when raising the exception
    """

    with handle_errors(
        f"something went wrong (specific example)",
        raise_exc_class=DerivedError,
        raise_args=["init arg"],
        raise_kwargs=dict(init_kwarg="init kwarg"),
    ):
        print("we are fine")
        raise ValueError("here we die")
        print("we should not get here")


if __name__ == '__main__':
    with wrap_demo("Demonstrating simple handle_errors example"):
        simple_handle_errors()

    with wrap_demo("Demonstrating absorbing handle_errors example"):
        absorbing_handle_errors()

    with wrap_demo("Demonstrating multiple handle_errors example"):
        multiple_handle_errors()

    with wrap_demo("Demonstrating specific handle_errors example"):
        specific_handle_errors()
