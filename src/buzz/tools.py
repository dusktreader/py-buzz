"""
This module supplies the core functions of the py-buzz package.
"""

from __future__ import annotations

import asyncio
import contextlib
import dataclasses
import functools
import random
import sys
import time
import types
from asyncio import iscoroutinefunction
from collections.abc import AsyncIterator, Coroutine, Iterable, Iterator, Mapping
from typing import Any, Callable, Literal, Protocol, TypeVar, cast, get_args, get_origin
from typing_extensions import TypeForm

TNonNull = TypeVar("TNonNull")


@dataclasses.dataclass
class ExcBuilderParams:
    """
    Dataclass for the `exc_builder` user supplied exception constructor.

    Attributes:

        raise_exc_class: The exception class that should be built
        message:         The message to build the exception with
        raise_args:      The positional arguments that are needed to build the exception
        raise_kwargs:    The keyword arguments that are needed to build the exception
        base_message:    An optional "base" message. This will carry the original message from:
                         - handle_errors
                         - check_expressions
    """

    raise_exc_class: type[Exception]
    message: str
    raise_args: Iterable[Any]
    raise_kwargs: Mapping[str, Any]
    base_message: str | None = None


@dataclasses.dataclass
class DoExceptParams:
    """
    Dataclass for the `do_except` user supplied handling method.

    Attributes:

        err:           The exception instance itself
        base_message:  The base message parameter that was passed to the `handle_errors()` function
        final_message: The final, combined message including the base message and string formatted exception
        trace:         A traceback of the exception
    """

    err: BaseException
    base_message: str
    final_message: str
    trace: types.TracebackType | None


# Callback Protocol types for better type hints and IDE support


class ExceptionCallback(Protocol):
    """Protocol for callbacks that receive a single exception."""

    def __call__(self, __exc: Exception, /) -> None:
        """Handle an exception."""
        ...


class DoExceptParamsCallback(Protocol):
    """Protocol for callbacks that receive DoExceptParams."""

    def __call__(self, __params: DoExceptParams, /) -> None:
        """Handle exception with full context."""
        ...


class NoArgCallback(Protocol):
    """Protocol for callbacks that take no arguments."""

    def __call__(self) -> None:
        """Execute callback with no arguments."""
        ...


class AsyncDoExceptParamsCallback(Protocol):
    """Protocol for async callbacks that receive DoExceptParams."""

    def __call__(self, __params: DoExceptParams, /) -> Coroutine[Any, Any, None]:
        """Handle exception with full context asynchronously."""
        ...


class AsyncNoArgCallback(Protocol):
    """Protocol for async callbacks that take no arguments."""

    def __call__(self) -> Coroutine[Any, Any, None]:
        """Execute callback with no arguments asynchronously."""
        ...


def default_exc_builder(params: ExcBuilderParams) -> Exception:
    """
    Build an exception instance using default behavior where message is passed as first positional argument.

    Some exception types such as FastAPI's HTTPException do not take a message as the first positional argument, so
    they will need a different exception builder.
    """
    return params.raise_exc_class(
        params.message,
        *params.raise_args,
        **params.raise_kwargs,
    )


def require_condition(
    expr: Any,
    message: str,
    raise_exc_class: type[Exception] = Exception,
    raise_args: Iterable[Any] | None = None,
    raise_kwargs: Mapping[str, Any] | None = None,
    exc_builder: Callable[[ExcBuilderParams], Exception] = default_exc_builder,
    do_except: ExceptionCallback | None = None,
    do_else: NoArgCallback | None = None,
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
                         an instance of the `raise_exc_class`.
        raise_kwargs:    Keyword args that will be passed when raising an instance of the `raise_exc_class`.
        exc_builder:     A function that should be called to construct the raised `raise_exc_class`. Useful for
                         exception classes that do not take a message as the first positional argument.
        do_except:       A function that should be called only if the condition fails.
                         Must accept one parameter that is the exception that will be raised.
                         If not provided, nothing will be done.
        do_else:         A function that should be called if the condition passes.
                         If not provided, nothing will be done.
    """

    if not expr:
        exc: Exception = exc_builder(
            ExcBuilderParams(
                raise_exc_class=raise_exc_class,
                message=message,
                raise_args=raise_args or [],
                raise_kwargs=raise_kwargs or {},
            )
        )
        if do_except:
            do_except(exc)
        raise exc
    elif do_else:
        do_else()


def enforce_defined(
    value: TNonNull | None,
    message: str = "Value was not defined (None)",
    raise_exc_class: type[Exception] = Exception,
    raise_args: Iterable[Any] | None = None,
    raise_kwargs: Mapping[str, Any] | None = None,
    exc_builder: Callable[[ExcBuilderParams], Exception] = default_exc_builder,
    do_except: ExceptionCallback | None = None,
    do_else: NoArgCallback | None = None,
) -> TNonNull:
    """
    Assert that a value is not None. If the assertion fails, raise an exception with the supplied message.

    Args:

        value:            The value that is checked to be non-null
        message:          The failure message to attach to the raised Exception
        raise_exc_class:  The exception type to raise with the constructed message if the expression is None.

                          Defaults to Exception.
                          May not be None.

        raise_args:       Additional positional args (after the constructed message) that will passed when raising
                          an instance of the `raise_exc_class`.
        raise_kwargs:     Keyword args that will be passed when raising an instance of the `raise_exc_class`.
        exc_builder:      A function that should be called to construct the raised `raise_exc_class`. Useful for
                          exception classes that do not take a message as the first positional argument.
        do_except:        A function that should be called only if value is not defined.
                          Must accept one parameter that is the exception that will be raised.
                          If not provided, nothing will be done.
        do_else:          A function that should be called if the value is defined.
                          If not provided, nothing will be done.
    """
    if value is not None:
        if do_else:
            do_else()
        return value
    else:
        exc: Exception = exc_builder(
            ExcBuilderParams(
                raise_exc_class=raise_exc_class,
                message=message,
                raise_args=raise_args or [],
                raise_kwargs=raise_kwargs or {},
            )
        )
        if do_except:
            do_except(exc)
        raise exc


EnsuredType = TypeVar("EnsuredType")


def ensure_type(
    value: Any,
    type_: type[EnsuredType],
    message: str | None = None,
    raise_exc_class: type[Exception] = Exception,
    raise_args: Iterable[Any] | None = None,
    raise_kwargs: Mapping[str, Any] | None = None,
    exc_builder: Callable[[ExcBuilderParams], Exception] = default_exc_builder,
    do_except: ExceptionCallback | None = None,
    do_else: NoArgCallback | None = None,
) -> EnsuredType:
    """
    Assert that a value is of a specific type. If the assertion fails, raise an exception with the supplied message.

    Args:

        value:            The value that is to be checked
        type_:            The type that the value must be of
        message:          The failure message to attach to the raised Exception
        raise_exc_class:  The exception type to raise with the constructed message if the type does not match

                          Defaults to Exception
                          May not be None

        raise_args:       Additional positional args (after the constructed message) that will passed when raising
                          an instance of the `raise_exc_class`.
        raise_kwargs:     Keyword args that will be passed when raising an instance of the `raise_exc_class`.
        exc_builder:      A function that should be called to construct the raised `raise_exc_class`. Useful for
                          exception classes that do not take a message as the first positional argument.
        do_except:        A function that should be called only if value is of the wrong type.
                          Must accept one parameter that is the exception that will be raised.
                          If not provided, nothing will be done.
        do_else:          A function that should be called if the value is of the correct type.
                          If not provided, nothing will be done.
    """
    if not message:
        message = f"Value was not of type {type_}"
    matches = isinstance(value, type_)

    if matches:
        if do_else:
            do_else()
        return value
    else:
        exc: Exception = exc_builder(
            ExcBuilderParams(
                raise_exc_class=raise_exc_class,
                message=message,
                raise_args=raise_args or [],
                raise_kwargs=raise_kwargs or {},
            )
        )
        if do_except:
            do_except(exc)
        raise exc


LiteralElement = TypeVar("LiteralElement", int, bool, str, bytes, None)


def verify_literal(
    value: object,
    literal_type: TypeForm[LiteralElement],  # ty: ignore[invalid-type-form]  # Remove on support of TypeForm (PEP 747)
    message: str | None = None,
    raise_exc_class: type[Exception] = Exception,
    raise_args: Iterable[Any] | None = None,
    raise_kwargs: Mapping[str, Any] | None = None,
    exc_builder: Callable[[ExcBuilderParams], Exception] = default_exc_builder,
    do_except: ExceptionCallback | None = None,
    do_else: NoArgCallback | None = None,
) -> LiteralElement:
    """
    Assert that a value is one of the allowed values of a `typing.Literal` type. If the assertion fails, raise an
    exception with the supplied message.

    Args:

        value:            The value that is to be checked
        literal_type:     A `typing.Literal` type whose allowed values the value must be one of
        message:          The failure message to attach to the raised Exception
        raise_exc_class:  The exception type to raise with the constructed message if the value does not match

                          Defaults to Exception
                          May not be None

        raise_args:       Additional positional args (after the constructed message) that will passed when raising
                          an instance of the `raise_exc_class`.
        raise_kwargs:     Keyword args that will be passed when raising an instance of the `raise_exc_class`.
        exc_builder:      A function that should be called to construct the raised `raise_exc_class`. Useful for
                          exception classes that do not take a message as the first positional argument.
        do_except:        A function that should be called only if value is not one of the allowed values.
                          Must accept one parameter that is the exception that will be raised.
                          If not provided, nothing will be done.
        do_else:          A function that should be called if the value is one of the allowed values.
                          If not provided, nothing will be done.
    """
    if get_origin(literal_type) is not Literal:
        raise TypeError(f"type_ must be a Literal type, got {literal_type!r}")
    literal_values = get_args(literal_type)
    if not message:
        message = f"Value was not one of the allowed literal values: {literal_values}"

    if value in literal_values:
        if do_else:
            do_else()
        return cast(LiteralElement, value)
    else:
        exc: Exception = exc_builder(
            ExcBuilderParams(
                raise_exc_class=raise_exc_class,
                message=message,
                raise_args=raise_args or [],
                raise_kwargs=raise_kwargs or {},
            )
        )
        if do_except:
            do_except(exc)
        raise exc


class _ExpressionChecker:
    """
    A utility class to be used with the `check_expressions` context manager.
    """

    problems: list[str]
    expression_counter: int

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
    base_message: str,
    raise_exc_class: type[Exception] = Exception,
    raise_args: Iterable[Any] | None = None,
    raise_kwargs: Mapping[str, Any] | None = None,
    exc_builder: Callable[[ExcBuilderParams], Exception] = default_exc_builder,
    do_except: ExceptionCallback | None = None,
    do_else: NoArgCallback | None = None,
):
    """
    Check a series of expressions inside of a context manager. If any fail an exception is raised that contains a
    main message and a description of each failing expression.

    Args:
        base_message:      The base failure message to include in the constructed message that is passed to the
                           raised Exception. Will be included in `ExcBuilderParams` passed to `exc_builder`.
        raise_exc_class:   The exception type to raise with the assembled message if any of the expressions are falsey.

                           Defaults to Exception.

                           May not be None.
        raise_args:        Additional positional args (after the assembled message) that will passed when raising
                           an instance of the `raise_exc_class`.
        raise_kwargs:      Keyword args that will be passed when raising an instance of the `raise_exc_class`.
        exc_builder:       A function that should be called to construct the raised `raise_exc_class`. Useful for
                           exception classes that do not take a message as the first positional argument.
        do_except:         A function that should be called only if the any of the expressions are falsey.
                           Must accept one parameter that is the exception that will be raised.
                           If not provided, nothing will be done.
        do_else:           A function that should be called if none of the the expressions are falsey.
                           If not provided, nothing will be done.

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

    checker = _ExpressionChecker()
    yield checker.check
    message = "\n  ".join(
        [
            f"Checked expressions failed: {base_message}",
            *checker.problems,
        ]
    )

    if len(checker.problems) > 0:
        exc: Exception = exc_builder(
            ExcBuilderParams(
                raise_exc_class=raise_exc_class,
                message=message,
                raise_args=raise_args or [],
                raise_kwargs=raise_kwargs or {},
                base_message=base_message,
            )
        )
        if do_except:
            do_except(exc)
        raise exc
    elif do_else:
        do_else()


def reformat_exception(message: str, err: BaseException) -> str:
    """
    Reformat an exception by adding a message to it and reporting the original exception name and message.
    """
    return f"{message} -- {type(err).__name__}: {str(err)}"


def get_traceback() -> types.TracebackType | None:
    """
    Retrieves the traceback after an exception has been raised.
    """
    return sys.exc_info()[2]


@contextlib.contextmanager
def handle_errors(
    base_message: str,
    raise_exc_class: type[Exception] | None = Exception,
    raise_args: Iterable[Any] | None = None,
    raise_kwargs: Mapping[str, Any] | None = None,
    handle_exc_class: type[Exception] | tuple[type[Exception], ...] = Exception,
    ignore_exc_class: type[Exception] | tuple[type[Exception], ...] | None = None,
    do_finally: NoArgCallback | None = None,
    do_except: DoExceptParamsCallback | None = None,
    do_else: NoArgCallback | None = None,
    exc_builder: Callable[[ExcBuilderParams], Exception] = default_exc_builder,
) -> Iterator[None]:
    """
    Provide a context manager that will intercept exceptions and repackage them in a new exception with a message
    attached that combines the base message along with the message from the handled exception:

    Args:
        base_message:      The base message to attach to the raised exception. Will be included in `ExcBuilderParams`
                           passed to `exc_builder`.
        raise_exc_class:   The exception type to raise with the constructed message if an exception is caught in the
                           managed context. If `None` is passed, no new exception will be raised and only the
                           `do_except`, `do_else`, and `do_finally` functions will be called.
        raise_args:        Additional positional args (after the constructed message) that will passed when raising
                           an instance of the `raise_exc_class`.
        raise_kwargs:      Keyword args that will be passed when raising an instance of the `raise_exc_class`.
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
                           If not provided, nothing will be done.
        do_except:         A function that should be called only if there was an exception. Must accept one
                           parameter that is an instance of the `DoExceptParams` dataclass.
                           Note that the `do_except` method is passed the *original exception*.
                           If not provided, nothing will be done.
        do_else:           A function that should be called only if there were no exceptions encountered.
                           If not provided, nothing will be done.
        exc_builder:       A function that should be called to construct the raised `raise_exc_class`. Useful for
                           exception classes that do not take a message as the first positional argument.

    Example:

        The following is an example usage:

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
            final_message = reformat_exception(base_message, err)
        except Exception as msg_err:
            raise RuntimeError(f"Failed while formatting message: {repr(msg_err)}")

        trace = get_traceback()

        if do_except:
            do_except(
                DoExceptParams(
                    err=err,
                    base_message=base_message,
                    final_message=final_message,
                    trace=trace,
                )
            )
        if raise_exc_class is not None:
            raise exc_builder(
                ExcBuilderParams(
                    raise_exc_class=raise_exc_class,
                    message=final_message,
                    raise_args=raise_args or [],
                    raise_kwargs=raise_kwargs or {},
                    base_message=base_message,
                )
            ).with_traceback(trace) from err
    else:
        if do_else:
            do_else()
    finally:
        if do_finally:
            do_finally()


@contextlib.asynccontextmanager
async def handle_errors_async(
    base_message: str,
    raise_exc_class: type[Exception] | None = Exception,
    raise_args: Iterable[Any] | None = None,
    raise_kwargs: Mapping[str, Any] | None = None,
    handle_exc_class: type[Exception] | tuple[type[Exception], ...] = Exception,
    ignore_exc_class: type[Exception] | tuple[type[Exception], ...] | None = None,
    do_finally: NoArgCallback | AsyncNoArgCallback | None = None,
    do_except: DoExceptParamsCallback | AsyncDoExceptParamsCallback | None = None,
    do_else: NoArgCallback | AsyncNoArgCallback | None = None,
    exc_builder: Callable[[ExcBuilderParams], Exception] = default_exc_builder,
) -> AsyncIterator[None]:
    """
    Provide an async context manager that will intercept exceptions and repackage them with a message attached:

    Args:
        base_message:      The base message to attach to the raised exception. Will be included in `ExcBuilderParams`
                           passed to `exc_builder`.
        raise_exc_class:   The exception type to raise with the constructed message if an exception is caught in the
                           managed context. If `None` is passed, no new exception will be raised and only the
                           `do_except`, `do_else`, and `do_finally` functions will be called.
        raise_args:        Additional positional args (after the constructed message) that will passed when raising
                           an instance of the `raise_exc_class`.
        raise_kwargs:      Keyword args that will be passed when raising an instance of the `raise_exc_class`.
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
                           May be an async function.
                           If not provided, nothing will be done.
        do_except:         A function that should be called only if there was an exception. Must accept one
                           parameter that is an instance of the `DoExceptParams` dataclass.
                           May be an async function.
                           Note that the `do_except` method is passed the *original exception*.
                           If not provided, nothing will be done.
        do_else:           A function that should be called only if there were no exceptions encountered.
                           May be an async function.
                           If not provided, nothing will be done.
        exc_builder:       A function that should be called to construct the raised `raise_exc_class`. Useful for
                           exception classes that do not take a message as the first positional argument.

    Example:

        The following is an example usage:

            async with handle_errors("It didn't work"):
                await some_code_that_might_raise_an_exception()
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
            final_message = reformat_exception(base_message, err)
        except Exception as msg_err:
            raise RuntimeError(f"Failed while formatting message: {repr(msg_err)}")

        trace = get_traceback()

        if iscoroutinefunction(do_except):
            await do_except(
                DoExceptParams(
                    err=err,
                    base_message=base_message,
                    final_message=final_message,
                    trace=trace,
                )
            )
        else:
            if do_except:
                do_except(
                    DoExceptParams(
                        err=err,
                        base_message=base_message,
                        final_message=final_message,
                        trace=trace,
                    )
                )

        if raise_exc_class is not None:
            raise exc_builder(
                ExcBuilderParams(
                    raise_exc_class=raise_exc_class,
                    message=final_message,
                    raise_args=raise_args or [],
                    raise_kwargs=raise_kwargs or {},
                    base_message=base_message,
                )
            ).with_traceback(trace) from err
    else:
        if do_else:
            if iscoroutinefunction(do_else):
                await do_else()
            else:
                do_else()
    finally:
        if do_finally:
            if iscoroutinefunction(do_finally):
                await do_finally()
            else:
                do_finally()


class RetryCallback(Protocol):
    """Protocol for retry callbacks."""

    def __call__(self, __attempt: int, __exception: BaseException, /) -> None:
        """
        Callback invoked on each retry attempt.

        Args:
            __attempt: The current attempt number (1-indexed)
            __exception: The exception that triggered the retry
        """
        ...


TReturnType = TypeVar("TReturnType")


def _calculate_delay(attempt: int, backoff: float, max_delay: float, jitter: bool) -> float:
    """
    Calculate the delay before the next retry attempt.

    Args:
        attempt: The current attempt number (0-indexed for calculation)
        backoff: Exponential backoff multiplier
        max_delay: Maximum delay in seconds
        jitter: Whether to add random jitter

    Returns:
        Delay in seconds
    """
    delay = backoff**attempt
    delay = min(delay, max_delay)
    if jitter:
        delay = random.uniform(0, delay)
    return delay


def retry(
    message: str,
    max_attempts: int = 3,
    backoff: float = 2.0,
    max_delay: float = 60.0,
    jitter: bool = True,
    retry_on: type[Exception] | tuple[type[Exception], ...] = Exception,
    raise_exc_class: type[Exception] = Exception,
    raise_args: Iterable[Any] | None = None,
    raise_kwargs: Mapping[str, Any] | None = None,
    exc_builder: Callable[[ExcBuilderParams], Exception] = default_exc_builder,
    on_retry: RetryCallback | None = None,
) -> Callable[[Callable[..., TReturnType]], Callable[..., TReturnType]]:
    """
    Decorator that retries a function on failure with exponential backoff.

    Args:
        message:          Message for final exception. Supports {attempts} placeholder.
        max_attempts:     Maximum number of attempts (including initial attempt). Must be >= 1.
        backoff:          Exponential backoff multiplier. Delay = backoff^attempt.
        max_delay:        Maximum delay between retries in seconds.
        jitter:           Add random jitter to prevent thundering herd.
        retry_on:         Exception type(s) to retry. Other exceptions will be raised immediately.
        raise_exc_class:  Exception type to raise on final failure.
        raise_args:       Additional positional args for the raised exception.
        raise_kwargs:     Keyword args for the raised exception.
        exc_builder:      Function to construct the exception.
        on_retry:         Optional callback invoked on each retry with (attempt, exception).

    Returns:
        Decorated function that retries on failure.

    Example:
        @retry("Failed to fetch data after {attempts} attempts", max_attempts=3, backoff=2.0, retry_on=(ConnectionError, TimeoutError))
        def fetch_data(url):
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
    """
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    def decorator(func: Callable[..., TReturnType]) -> Callable[..., TReturnType]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> TReturnType:
            last_exception: BaseException | None = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except retry_on as exc:
                    last_exception = exc

                    if attempt + 1 >= max_attempts:
                        break

                    if on_retry:
                        on_retry(attempt + 1, exc)

                    delay = _calculate_delay(attempt, backoff, max_delay, jitter)
                    time.sleep(delay)

            final_message = message.format(attempts=max_attempts)
            if last_exception:
                final_message = reformat_exception(final_message, last_exception)

            raise exc_builder(
                ExcBuilderParams(
                    raise_exc_class=raise_exc_class,
                    message=final_message,
                    raise_args=raise_args or [],
                    raise_kwargs=raise_kwargs or {},
                )
            ) from last_exception

        return wrapper

    return decorator


def retry_async(
    message: str,
    max_attempts: int = 3,
    backoff: float = 2.0,
    max_delay: float = 60.0,
    jitter: bool = True,
    retry_on: type[Exception] | tuple[type[Exception], ...] = Exception,
    raise_exc_class: type[Exception] = Exception,
    raise_args: Iterable[Any] | None = None,
    raise_kwargs: Mapping[str, Any] | None = None,
    exc_builder: Callable[[ExcBuilderParams], Exception] = default_exc_builder,
    on_retry: RetryCallback | None = None,
) -> Callable[[Callable[..., Coroutine[Any, Any, TReturnType]]], Callable[..., Coroutine[Any, Any, TReturnType]]]:
    """
    Decorator that retries an async function on failure with exponential backoff.

    Args:
        message:          Message for final exception. Supports {attempts} placeholder.
        max_attempts:     Maximum number of attempts (including initial attempt). Must be >= 1.
        backoff:          Exponential backoff multiplier. Delay = backoff^attempt.
        max_delay:        Maximum delay between retries in seconds.
        jitter:           Add random jitter to prevent thundering herd.
        retry_on:         Exception type(s) to retry. Other exceptions will be raised immediately.
        raise_exc_class:  Exception type to raise on final failure.
        raise_args:       Additional positional args for the raised exception.
        raise_kwargs:     Keyword args for the raised exception.
        exc_builder:      Function to construct the exception.
        on_retry:         Optional callback invoked on each retry with (attempt, exception).

    Returns:
        Decorated async function that retries on failure.

    Example:
        @retry_async("Failed to fetch data after {attempts} attempts", max_attempts=3, backoff=2.0, retry_on=(ConnectionError, TimeoutError))
        async def fetch_data(url):
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    return await response.json()
    """
    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1")

    def decorator(
        func: Callable[..., Coroutine[Any, Any, TReturnType]],
    ) -> Callable[..., Coroutine[Any, Any, TReturnType]]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> TReturnType:
            last_exception: BaseException | None = None

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except retry_on as exc:
                    last_exception = exc

                    if attempt + 1 >= max_attempts:
                        break

                    if on_retry:
                        on_retry(attempt + 1, exc)

                    delay = _calculate_delay(attempt, backoff, max_delay, jitter)
                    await asyncio.sleep(delay)

            final_message = message.format(attempts=max_attempts)
            if last_exception:
                final_message = reformat_exception(final_message, last_exception)

            raise exc_builder(
                ExcBuilderParams(
                    raise_exc_class=raise_exc_class,
                    message=final_message,
                    raise_args=raise_args or [],
                    raise_kwargs=raise_kwargs or {},
                )
            ) from last_exception

        return wrapper

    return decorator
