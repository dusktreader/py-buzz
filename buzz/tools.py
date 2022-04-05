"""
This module supplies the core functions of the py-buzz package.

Includes:

* require_condition:  asserts a condition and raises an exception otherwise
* handle_errors:      a context manager that handles exceptions
* check_expressions:  a context manager that checks multiple expressions
"""
import contextlib
import dataclasses
import sys
import types
from typing import Any, Callable, Iterable, Iterator, Mapping, Optional, Tuple, Type, Union


def noop(*_, **__):
    pass


def require_condition(
    expr: Any,
    message: str,
    raise_exc_class: Type[Exception] = Exception,
    raise_args: Optional[Iterable[Any]] = None,
    raise_kwargs: Optional[Mapping[str, Any]] = None,
):
    """
    Assert that an expression is truthy. If the assertion fails, raise an exception with the supplied message.

    :param: message:          The failure message to attach to the raised Exception
    :param: expr:             The value that is checked for truthiness (usually an evaluated expression)
    :param: raise_exc_class:  The exception type to raise with the constructed message if the expression is falsey.

                              Defaults to Exception.
                              May not be None.

    :param: raise_args:       Additional positional args (after the constructed message) that will passed when raising
                              an instance of the ``raise_exc_class``.
    :param: raise_kwargs:     Keyword args that will be passed when raising an instance of the ``raise_exc_class``.
    """
    if raise_exc_class is None:
        raise ValueError("The raise_exc_class kwarg may not be None")

    if not expr:
        args = raise_args or []
        kwargs = raise_kwargs or {}
        raise raise_exc_class(message, *args, **kwargs)


class _ExpressionChecker:
    """
    A utility class to be used with the ``check_expressions`` context manager.
    """

    def __init__(self):
        self.problems = []
        self.expression_counter = 0

    @staticmethod
    def ordinalize(n: int) -> str:
        """
        Adapted from the awesome inflection library (https://github.com/jpvanhal/inflection)
        """
        if 11 <= n % 100 <= 13:
            return f"{n}th"
        else:
            return {
                1: f"{n}st",
                2: f"{n}nd",
                3: f"{n}rd",
            }.get(n % 10, f"{n}th")

    def check(self, evaluated_expression: Any, message: str = None):
        self.expression_counter += 1
        if not evaluated_expression:
            if message is None:
                message = "{nth} expression failed".format(nth=self.ordinalize(self.expression_counter))
            self.problems.append(f"{self.expression_counter}: {message}")


@contextlib.contextmanager
def check_expressions(
    main_message: str,
    raise_exc_class: Type[Exception] = Exception,
    raise_args: Optional[Iterable[Any]] = None,
    raise_kwargs: Optional[Mapping[str, Any]] = None,
):
    """
    Check a series of expressions inside of a context manager. If any fail an exception is raised that contains a
    main message and a description of each failing expression.

    :param: main message:      The main failure message to include in the constructed message that is passed to the
                               raised Exception
    :param: raise_exc_class:   The exception type to raise with the constructed message if the expression is falsey.

                               Defaults to Exception.

                               May not be None.
    :param: raise_args:        Additional positional args (after the constructed message) that will passed when raising
                               an instance of the ``raise_exc_class``.
    :param: raise_kwargs:      Keyword args that will be passed when raising an instance of the ``raise_exc_class``.

    Example:

    .. code-block:: python

       with check_expressions("Something wasn't right") as check:
           check(a is not None)
           check(a > b, "a must be greater than b")
           check(a != 1, "a must not equal 1")
           check(b >= 0, "b must not be negative")

    This would render output like:

    .. code-block:: bash

       Checked expressions failed: Something wasn't right:
         1: first expressoin failed
         3: a must not equal 1
    """
    if raise_exc_class is None:
        raise ValueError("The raise_exc_class kwarg may not be None")

    checker = _ExpressionChecker()
    yield checker.check
    message = "\n  ".join(
        [
            f"Checked expressions failed: {main_message}",
            *checker.problems,
        ]
    )

    require_condition(
        len(checker.problems) == 0,
        message,
        raise_exc_class=raise_exc_class,
        raise_args=raise_args,
        raise_kwargs=raise_kwargs,
    )


def reformat_exception(message: str, err: Exception) -> str:
    """
    Reformat an exception by adding a message to it and reporting the original exception name and message.
    """
    return f"{message} -- {type(err).__name__}: {str(err)}"


def get_traceback() -> Union[types.TracebackType, None]:
    """
    Retrieves the traceback after an exception has been raised.
    """
    return sys.exc_info()[2]


@dataclasses.dataclass
class DoExceptParams:
    """
    Dataclass for the ``do_except`` user supplied handling method.
    """

    err: Exception
    final_message: str
    trace: Optional[types.TracebackType]


@contextlib.contextmanager
def handle_errors(
    message: str,
    raise_exc_class: Union[Type[Exception], None] = Exception,
    raise_args: Optional[Iterable[Any]] = None,
    raise_kwargs: Optional[Mapping[str, Any]] = None,
    handle_exc_class: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
    do_finally: Callable[[], None] = noop,
    do_except: Callable[[DoExceptParams], None] = noop,
    do_else: Callable[[], None] = noop,
) -> Iterator[None]:
    """
    Provide a context manager that will intercept exceptions and repackage them with a message attached:

    Example:

    .. code-block:: python

       with handle_errors("It didn't work"):
           some_code_that_might_raise_an_exception()

    :param: message:           The message to attach to the raised exception.
    :param: raise_exc_class:   The exception type to raise with the constructed message if an exception is caught in the
                               managed context.

                               Defaults to Exception.

                               If ``None`` is passed, no new exception will be raised and only the ``do_except``,
                               ``do_else``, and ``do_finally`` functions will be called.
    :param: raise_args:        Additional positional args (after the constructed message) that will passed when raising
                               an instance of the ``raise_exc_class``.
    :param: raise_kwargs:      Keyword args that will be passed when raising an instance of the ``raise_exc_class``.
    :param: handle_exc_class:  Limits the class of exceptions that will be intercepted
                               Any other exception types will not be caught and re-packaged.
                               Defaults to Exception (will handle all exceptions). May also be provided as a tuple
                               of multiple exception types to handle.
    :param: do_finally:        A function that should always be called at the end of the block.
                               Should take no parameters.
    :param: do_except:         A function that should be called only if there was an exception. Must accept one
                               parameter that is an instance of the ``DoExceptParams`` dataclass.
                               Note that the ``do_except`` method is passed the *original exception*.
    :param: do_else:           A function taht should be called only if there were no exceptions encountered.
    """
    try:
        yield
    except handle_exc_class as err:
        try:
            final_message = reformat_exception(message, err)
        except Exception as msg_err:
            raise RuntimeError(f"Failed while formatting message: {repr(msg_err)}")

        trace = get_traceback()

        do_except(DoExceptParams(err, final_message, trace))  # type: ignore # For packport of dataclasses in python3.6
        if raise_exc_class is not None:
            args = raise_args or []
            kwargs = raise_kwargs or {}
            raise raise_exc_class(final_message, *args, **kwargs).with_traceback(trace) from err
    else:
        do_else()
    finally:
        do_finally()
