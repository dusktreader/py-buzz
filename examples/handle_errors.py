"""
This example set demonstrates the use of the handle_errors context manager.
The handle_errors context manager effectively wraps a block of code with
a try-except without having to explicitly declare them. Additionally, it wraps
all caught exceptions from the block in custom error messages
"""

from buzz import Buzz
from sys import argv
from traceback import format_tb


class HandleError(Buzz):
    pass


def simple_handle_errors():
    """
    This function demonstrates the simplest use of the handle_errors ctx_mgr.
    Note how the nested exception type is ValueError. The error produced by
    the handle_errors ctx_mgr should be of type HandleError. The resulting
    exception message will include the message supplied to the handle_error
    ctx_mgr as well as the message of the nested exception
    """
    print("Demonstrating simple handle_errors example")
    with HandleError.handle_errors("something went wrong (simple example)"):
        print("we are fine")
        raise ValueError("here we die")
        print("we should not get here")


def complex_handle_errors():
    """
    This function demonstrates a more complex usage of the handle_errors
    ctx_mgr. The following features are demonstrated::

      * Handling a specific exception type with ``exception_class``
      * Absorbing exceptions by setting ``re_raise`` to ``False``
      * Branching with ``do_except``, ``do_else``, and ``do_finally``
    """
    print("Demonstrating complex handle_errors example")

    def _handler_function(err, final_message, trace):
        """
        This function is a helper function for handling an exception from
        the handle_errors ctx_mgr.
        """
        print("Handling exception")
        print("==================")
        print("Final Message")
        print("-------------")
        print(final_message)
        print("Traceback")
        print("---------")
        print(''.join(format_tb(trace)))

    with HandleError.handle_errors(
            "something went wrong ({example_type})",
            example_type='complex example',
            re_raise=False,
            do_except=_handler_function,
            do_else=lambda: print('No exception occurred'),
            do_finally=lambda: print('Finished handling exceptions'),
    ):
        print("we are fine")
        raise ValueError("here we die")
        print("we should not get here")


if __name__ == '__main__':
    if len(argv) == 1 or argv[1] == 'simple':
        simple_handle_errors()
    elif argv[1] == 'complex':
        complex_handle_errors()
    else:
        print("No example selected. Call with one arg: 'simple' or 'complex'")
