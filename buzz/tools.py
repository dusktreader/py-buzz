"""
This module supplies the core functions of the py-buzz package.
"""

from __future__ import annotations

import contextlib
import dataclasses
import sys
import types
from typing import Any, Callable, Iterable, Iterator, Mapping, Tuple, TypeVar


def noop(*_, **__):
    pass


TExc = TypeVar("TExc", bound=Exception)


def default_exc_builder(exc: type[TExc], message: str, *args, **kwargs) -> TExc:
    """
    Build an exception instance using default behavior where message is passed as first positional argument.

    Some exception types such as FastAPI's HTTPException do not take a message as the first positional argument, so
    they will need a different exception builder.
    """
    return exc(message, *args, **kwargs)


def require_condition(
    expr: Any,
    message: str,
    raise_exc_class: type[Exception] = Exception,
    raise_args: Iterable[Any] | None = None,
    raise_kwargs: Mapping[str, Any] | None = None,
    exc_builder: Callable[..., Exception] = default_exc_builder,
):
    """
    Assert that an expression is truthy. If the assertion fails, raise an exception with the supplied message.

    Args:

        message:         The failure message to attach to the raised Exception
        expr:            The value that is checked for truthiness (usually an evaluated expression)
        raise_exc_class: The exception type to raise with the constructed message if the expression is falsey.
                         Defaults to Exception.
                         May not be None.
        raise_args:      Additional positional args (after the constructed message) that will passed when raising
                         an instance of the ``raise_exc_class``.
        raise_kwargs:    Keyword args that will be passed when raising an instance of the ``raise_exc_class``.
    """
    if raise_exc_class is None:
        raise ValueError("The raise_exc_class kwarg may not be None")

    if not expr:
        args = raise_args or []
        kwargs = raise_kwargs or {}
        raise exc_builder(raise_exc_class, message, *args, **kwargs)


TNonNull = TypeVar("TNonNull")


def enforce_defined(
    value: TNonNull | None,
    message: str = "Value was not defined (None)",
    raise_exc_class: type[Exception] = Exception,
    raise_args: Iterable[Any] | None = None,
    raise_kwargs: Mapping[str, Any] | None = None,
    exc_builder: Callable[..., Exception] = default_exc_builder,
) -> TNonNull:
    """
    Assert that a value is not None. If the assertion fails, raise an exception with the supplied message.

    Args:

        value:            The value that is checked to be non-null
        message:          The failure message to attach to the raised Exception
        expr:             The value that is checked for truthiness (usually an evaluated expression)
        raise_exc_class:  The exception type to raise with the constructed message if the expression is falsey.

                          Defaults to Exception.
                          May not be None.

        raise_args:       Additional positional args (after the constructed message) that will passed when raising
                          an instance of the ``raise_exc_class``.
        raise_kwargs:     Keyword args that will be passed when raising an instance of the ``raise_exc_class``.
    """
    if value is not None:
        return value
    else:
        args = raise_args or []
        kwargs = raise_kwargs or {}
        raise exc_builder(raise_exc_class, message, *args, **kwargs)


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

    def check(self, evaluated_expression: Any, message: str | None = None):
        self.expression_counter += 1
        if not evaluated_expression:
            if message is None:
                message = "{nth} expression failed".format(nth=self.ordinalize(self.expression_counter))
            self.problems.append(f"{self.expression_counter}: {message}")


@contextlib.contextmanager
def check_expressions(
    main_message: str,
    raise_exc_class: type[Exception] = Exception,
    raise_args: Iterable[Any] | None = None,
    raise_kwargs: Mapping[str, Any] | None = None,
    exc_builder: Callable[..., Exception] = default_exc_builder,
):
    """
    Check a series of expressions inside of a context manager. If any fail an exception is raised that contains a
    main message and a description of each failing expression.

    Args:
        main message:      The main failure message to include in the constructed message that is passed to the
                           raised Exception
        raise_exc_class:   The exception type to raise with the constructed message if the expression is falsey.

                           Defaults to Exception.

                           May not be None.
        raise_args:        Additional positional args (after the constructed message) that will passed when raising
                           an instance of the ``raise_exc_class``.
        raise_kwargs:      Keyword args that will be passed when raising an instance of the ``raise_exc_class``.

    Example:

        The following is an example usage::

            with check_expressions("Something wasn't right") as check:
                check(a is not None)
                check(a > b, "a must be greater than b")
                check(a != 1, "a must not equal 1")
                check(b >= 0, "b must not be negative")

        This would render output like::

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
        exc_builder=exc_builder,
    )


def reformat_exception(message: str, err: Exception) -> str:
    """
    Reformat an exception by adding a message to it and reporting the original exception name and message.
    """
    return f"{message} -- {type(err).__name__}: {str(err)}"


def get_traceback() -> types.TracebackType | None:
    """
    Retrieves the traceback after an exception has been raised.
    """
    return sys.exc_info()[2]


@dataclasses.dataclass
class DoExceptParams:
    """
    Dataclass for the `do_except` user supplied handling method.

    Attributes:

        err:           The exception instance itself.
        final_message: The final, combined message
        trace:         A traceback of the exception
    """

    err: Exception
    final_message: str
    trace: types.TracebackType | None


@contextlib.contextmanager
def handle_errors(
    message: str,
    raise_exc_class: type[Exception] | None = Exception,
    raise_args: Iterable[Any] | None = None,
    raise_kwargs: Mapping[str, Any] | None = None,
    handle_exc_class: type[Exception] | Tuple[type[Exception], ...] = Exception,
    ignore_exc_class: type[Exception] | Tuple[type[Exception], ...] | None = None,
    do_finally: Callable[[], None] = noop,
    do_except: Callable[[DoExceptParams], None] = noop,
    do_else: Callable[[], None] = noop,
    exc_builder: Callable[..., Exception] = default_exc_builder,
) -> Iterator[None]:
    """
    Provide a context manager that will intercept exceptions and repackage them with a message attached:

    Args:
        message:           The message to attach to the raised exception.
        raise_exc_class:   The exception type to raise with the constructed message if an exception is caught in the
                           managed context.

                           Defaults to Exception.

                           If ``None`` is passed, no new exception will be raised and only the ``do_except``,
                           ``do_else``, and ``do_finally`` functions will be called.
        raise_args:        Additional positional args (after the constructed message) that will passed when raising
                           an instance of the ``raise_exc_class``.
        raise_kwargs:      Keyword args that will be passed when raising an instance of the ``raise_exc_class``.
        handle_exc_class:  Limits the class of exceptions that will be intercepted
                           Any other exception types will not be caught and re-packaged.
                           Defaults to Exception (will handle all exceptions). May also be provided as a tuple
                           of multiple exception types to handle.
        ignore_exc_class:  Defines an exception or set of exception types that should not be handled at all.
                           Any matching exception types will be immediately re-raised. They will not be handled by
                           the `handle_errors` context manager at all. This is useful if you want a specific variant of
                           your `handle_exc_class` to not be handled by `handle_errors`. For example, if you want to use
                           `handle_exc_class=Exception` but you do not want `handle_errors` to handle `RuntimeError`.
                           Then, you would set `ignore_exc_class=RuntimeError`.
        do_finally:        A function that should always be called at the end of the block.
                           Should take no parameters.
        do_except:         A function that should be called only if there was an exception. Must accept one
                           parameter that is an instance of the ``DoExceptParams`` dataclass.
                           Note that the ``do_except`` method is passed the *original exception*.
        do_else:           A function that should be called only if there were no exceptions encountered.

    Example:

        The following is an example usage::

            with handle_errors("It didn't work"):
                some_code_that_might_raise_an_exception()
    """

    class _DefaultIgnoreException(Exception):
        """
        Define a special exception class to use for the default ignore behavior.

        Basically, this exception type can't be extracted from this method (easily), and thus could never actually
        be raised in any other context. This is only created here to preserve the `try/except/except/else/finally`
        structure.
        """

        pass

    ignore_exc_class = _DefaultIgnoreException if ignore_exc_class is None else ignore_exc_class

    try:
        yield
    except ignore_exc_class:
        raise
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
            raise exc_builder(raise_exc_class, final_message, *args, **kwargs).with_traceback(trace) from err
    else:
        do_else()
    finally:
        do_finally()
