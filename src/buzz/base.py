"""
This module defines the Buzz base class.
"""

from __future__ import annotations

import sys
import textwrap
from collections.abc import Callable, Iterable, Mapping
from types import TracebackType
from typing import Any, AsyncContextManager, ContextManager, Coroutine, TypeVar

from typing_extensions import Self, override

if sys.version_info >= (3, 15):
    from typing import TypeForm
else:
    from typing_extensions import TypeForm

from buzz.tools import (
    AsyncDoExceptParamsCallback,
    AsyncNoArgCallback,
    DoExceptParamsCallback,
    ExcBuilderParams,
    ExceptionCallback,
    NoArgCallback,
    RetryCallback,
    check_expressions,
    enforce_defined,
    ensure_type,
    get_traceback,
    handle_errors,
    handle_errors_async,
    raise_from,
    require_condition,
    retry,
    retry_async,
    verify_literal,
)

TNonNull = TypeVar("TNonNull")
EnsuredType = TypeVar("EnsuredType")
LiteralElement = TypeVar("LiteralElement", int, bool, str, bytes, None)


class Buzz(Exception):
    """
    This provides a specialized exception class that wraps up all the buzz utility functions.
    """

    def __init__(self, message: str, *args: Any, base_message: str | None = None, **kwargs: Any):
        """
        Initialize the exception with a message.

        Also, dedent the supplied message.
        """
        self.message: str = textwrap.dedent(message).strip()
        self.base_message: str | None = base_message
        super().__init__(self.message, *args, **kwargs)

    @override
    def __str__(self):
        return self.message

    @override
    def __repr__(self):
        return self.__class__.__name__

    @classmethod
    def exc_builder(cls, params: ExcBuilderParams) -> Self:
        """
        Build an instance of this Buzz exception.

        This method is used by the other methods to construct the exception. Binds attributes from ExcBuilderParams
        including the base_message.
        """
        if params.raise_exc_class is not cls:
            raise RuntimeError("Buzz.exc_builder() included non-matching `raise_exc_class`!")

        return cls(
            params.message,
            *params.raise_args,
            base_message=params.base_message,
            **params.raise_kwargs,
        )

    @classmethod
    def require_condition(
        cls,
        expr: Any,
        message: str,
        raise_args: Iterable[Any] | None = None,
        raise_kwargs: Mapping[str, Any] | None = None,
        do_except: ExceptionCallback | None = None,
        do_else: NoArgCallback | None = None,
    ):
        """
        Assert that an expression is truty. If the assertion fails, raise an exception (instance of this class) with the
        supplied message.

        Args:

            message:         The failure message to attach to the raised Exception
            expr:            The value that is checked for truthiness (usually an evaluated expression)
            raise_args:      Additional positional args (after the constructed message) that will passed when raising
                             an instance of the `raise_exc_class`.
            raise_kwargs:    Keyword args that will be passed when raising an instance of the `raise_exc_class`.
            do_except:       A function that should be called only if the condition fails.
                             Must accept one parameter that is the exception that will be raised.
                             If not provided, nothing will be done.
            do_else:         A function that should be called if the condition passes.
                             If not provided, nothing will be done.
        """
        return require_condition(
            expr,
            message,
            raise_exc_class=cls,
            raise_args=raise_args,
            raise_kwargs=raise_kwargs,
            exc_builder=cls.exc_builder,
            do_except=do_except,
            do_else=do_else,
        )

    @classmethod
    def enforce_defined(
        cls,
        value: TNonNull | None,
        message: str = "Value was not defined (None)",
        raise_args: Iterable[Any] | None = None,
        raise_kwargs: Mapping[str, Any] | None = None,
        do_except: ExceptionCallback | None = None,
        do_else: NoArgCallback | None = None,
    ) -> TNonNull:
        """
        Assert that a value is not None. If the assertion fails, raise an exception (instance of this class) with the
        supplied message.

        Args:

            value:            The value that is checked to be non-null
            message:          The failure message to attach to the raised Exception
            expr:             The value that is checked for truthiness (usually an evaluated expression)
            raise_args:       Additional positional args (after the constructed message) that will passed when raising
                              an instance of the `raise_exc_class`.
            raise_kwargs:     Keyword args that will be passed when raising an instance of the `raise_exc_class`.
            do_except:        A function that should be called only if value is not defined.
                              Must accept one parameter that is the exception that will be raised.
                              If not provided, nothing will be done.
            do_else:          A function that should be called if the value is defined.
                              If not provided, nothing will be done.
        """
        return enforce_defined(
            value,
            message,
            raise_exc_class=cls,
            raise_args=raise_args,
            raise_kwargs=raise_kwargs,
            exc_builder=cls.exc_builder,
            do_except=do_except,
            do_else=do_else,
        )

    @classmethod
    def ensure_type(
        cls,
        value: Any,
        type_: type[EnsuredType],
        message: str = "Value was not of type {type_}",
        raise_args: Iterable[Any] | None = None,
        raise_kwargs: Mapping[str, Any] | None = None,
        do_except: ExceptionCallback | None = None,
        do_else: NoArgCallback | None = None,
    ) -> EnsuredType:
        """
        Assert that a value is of a specific type. If the assertion fails, raise an exception (instance of this class)
        with the supplied message.

        Args:

            value:            The value that is to be checked
            type_:            The type that the value must be of
            message:          The failure message to attach to the raised Exception
            raise_args:       Additional positional args (after the constructed message) that will passed when raising
                              an instance of the `raise_exc_class`.
            raise_kwargs:     Keyword args that will be passed when raising an instance of the `raise_exc_class`.
            do_except:        A function that should be called only if value is of the wrong type.
                              Must accept one parameter that is the exception that will be raised.
                              If not provided, nothing will be done.
            do_else:          A function that should be called if the value is of the wrong type.
                              If not provided, nothing will be done.
        """
        return ensure_type(
            value,
            type_,
            message=message,
            raise_exc_class=cls,
            raise_args=raise_args,
            raise_kwargs=raise_kwargs,
            exc_builder=cls.exc_builder,
            do_except=do_except,
            do_else=do_else,
        )

    @classmethod
    def verify_literal(
        cls,
        value: object,
        literal_type: TypeForm[LiteralElement],  # ty: ignore[invalid-type-form]
        message: str | None = None,
        raise_args: Iterable[Any] | None = None,
        raise_kwargs: Mapping[str, Any] | None = None,
        do_except: ExceptionCallback | None = None,
        do_else: NoArgCallback | None = None,
    ) -> LiteralElement:
        """
        Assert that a value is one of the allowed values of a `typing.Literal` type. If the assertion fails, raise an
        exception (instance of this class) with the supplied message.

        Args:

            value:            The value that is to be checked
            literal_type:     A `typing.Literal` type whose allowed values the value must be one of
            message:          The failure message to attach to the raised Exception
            raise_args:       Additional positional args (after the constructed message) that will passed when raising
                              an instance of the `raise_exc_class`.
            raise_kwargs:     Keyword args that will be passed when raising an instance of the `raise_exc_class`.
            do_except:        A function that should be called only if value is not one of the allowed values.
                              Must accept one parameter that is the exception that will be raised.
                              If not provided, nothing will be done.
            do_else:          A function that should be called if the value is one of the allowed values.
                              If not provided, nothing will be done.
        """
        return verify_literal(
            value,
            literal_type,
            message=message,
            raise_exc_class=cls,
            raise_args=raise_args,
            raise_kwargs=raise_kwargs,
            exc_builder=cls.exc_builder,
            do_except=do_except,
            do_else=do_else,
        )

    @classmethod
    def check_expressions(
        cls,
        base_message: str,
        raise_args: Iterable[Any] | None = None,
        raise_kwargs: Mapping[str, Any] | None = None,
        do_except: ExceptionCallback | None = None,
        do_else: NoArgCallback | None = None,
    ):
        """
        Check a series of expressions inside of a context manager. If any fail an exception (instance of this class) is
        raised that contains a main message and a description of each failing expression.

        Args:
            base_message:      The base failure message to include in the constructed message that is passed to the
                               raised Exception. Will be included in `ExcBuilderParams` passed to `exc_builder`.
            raise_args:        Additional positional args (after the constructed message) that will passed when raising
                               an instance of the `raise_exc_class`.
            raise_kwargs:      Keyword args that will be passed when raising an instance of the `raise_exc_class`.
            do_except:         A function that should be called only if the any of the expressions are falsey.
                               Must accept one parameter that is the exception that will be raised.
                               If not provided, nothing will be done.
            do_else:           A function that should be called if none of the the expressions are falsey.
                               If not provided, nothing will be done.

        Example:

            The following is an example usage::

                with Buzz.check_expressions("Something wasn't right") as check:
                    check(a is not None)
                    check(a > b, "a must be greater than b")
                    check(a != 1, "a must not equal 1")
                    check(b >= 0, "b must not be negative")

            This would render output like::

                Checked expressions failed: Something wasn't right:
                  1: first expressoin failed
                  3: a must not equal 1
        """
        return check_expressions(
            base_message,
            raise_exc_class=cls,
            raise_args=raise_args,
            raise_kwargs=raise_kwargs,
            exc_builder=cls.exc_builder,
            do_except=do_except,
            do_else=do_else,
        )

    @classmethod
    def handle_errors(
        cls,
        base_message: str,
        re_raise: bool = True,
        raise_args: Iterable[Any] | None = None,
        raise_kwargs: Mapping[str, Any] | None = None,
        handle_exc_class: type[BaseException] | tuple[type[BaseException], ...] = Exception,
        ignore_exc_class: type[BaseException] | tuple[type[BaseException], ...] | None = None,
        do_finally: NoArgCallback | None = None,
        do_except: DoExceptParamsCallback | None = None,
        do_else: NoArgCallback | None = None,
    ) -> ContextManager[None]:
        """
        Provide a context manager that will intercept exceptions and repackage them in a new exception (instance of this
        class) with a message attached that combines the base message along with the message from the handled exception:

        Args:
            base_message:      The base message included in the raised exception.
            re_raise:          If True (the default), raise an instance of this class after handling an exception. If
                               False, absorb handled exceptions. The `do_` callbacks still run.
            raise_args:        Additional positional arguments passed to the raised exception after the message.
            raise_kwargs:      Keyword arguments passed to the raised exception.
            handle_exc_class:  The exception type or types to catch and repackage. Defaults to `Exception` and its
                               subclasses. Other exceptions pass through unchanged.
            ignore_exc_class:  The exception type or types to immediately reraise without handling. This is useful when
                               `handle_exc_class=Exception` but a specific subclass, such as `RuntimeError`, must pass
                               through unchanged.
            do_finally:        A zero-argument callback that runs when the context exits, whether or not an exception
                               occurred.
            do_except:         A callback that receives a `DoExceptParams` instance when a handled exception occurs.
                               Its `err` attribute contains the original exception.
            do_else:           A zero-argument callback that runs only when the block exits without an exception.

        Example:

            The following is an example usage:

                with Buzz.handle_errors("It didn't work"):
                    some_code_that_might_raise_an_exception()
        """
        return handle_errors(
            base_message,
            raise_exc_class=cls if re_raise else None,
            raise_args=raise_args,
            raise_kwargs=raise_kwargs,
            handle_exc_class=handle_exc_class,
            ignore_exc_class=ignore_exc_class,
            do_finally=do_finally,
            do_except=do_except,
            do_else=do_else,
            exc_builder=cls.exc_builder,
        )

    @classmethod
    def handle_errors_async(
        cls,
        base_message: str,
        re_raise: bool = True,
        raise_args: Iterable[Any] | None = None,
        raise_kwargs: Mapping[str, Any] | None = None,
        handle_exc_class: type[BaseException] | tuple[type[BaseException], ...] = Exception,
        ignore_exc_class: type[BaseException] | tuple[type[BaseException], ...] | None = None,
        do_finally: NoArgCallback | AsyncNoArgCallback | None = None,
        do_except: DoExceptParamsCallback | AsyncDoExceptParamsCallback | None = None,
        do_else: NoArgCallback | AsyncNoArgCallback | None = None,
    ) -> AsyncContextManager[None]:
        """
        Provide an async context manager that intercepts and repackages exceptions as this class.

        Async callbacks are supported for `do_finally`, `do_except`, and `do_else`.
        """
        return handle_errors_async(
            base_message,
            raise_exc_class=cls if re_raise else None,
            raise_args=raise_args,
            raise_kwargs=raise_kwargs,
            handle_exc_class=handle_exc_class,
            ignore_exc_class=ignore_exc_class,
            do_finally=do_finally,
            do_except=do_except,
            do_else=do_else,
            exc_builder=cls.exc_builder,
        )

    @classmethod
    def raise_from(
        cls,
        base_message: str,
        err: BaseException,
        raise_args: Iterable[Any] | None = None,
        raise_kwargs: Mapping[str, Any] | None = None,
        final_message: str | None = None,
        trace: TracebackType | None = None,
    ) -> None:
        """
        Raise an instance of this Buzz exception from an existing exception.

        Args:
            base_message:  The base message to include in the raised exception.
            err:           The original exception to raise from.
            raise_args:    Additional positional arguments to pass to the raised exception.
            raise_kwargs:  Keyword arguments to pass to the raised exception.
            final_message: The message to use for the raised exception. If omitted, format it from `base_message`
                           and `err`.
            trace:         The traceback to attach to the raised exception. If omitted, use the active exception's
                           traceback.
        """
        raise_from(
            base_message,
            err,
            raise_exc_class=cls,
            raise_args=raise_args,
            raise_kwargs=raise_kwargs,
            exc_builder=cls.exc_builder,
            final_message=final_message,
            trace=trace,
        )

    @classmethod
    def get_traceback(cls, *args: Any, **kwargs: Any):
        """
        Call the `get_traceback()` function.
        """
        return get_traceback(*args, **kwargs)

    @classmethod
    def retry(
        cls,
        message: str,
        max_attempts: int = 3,
        backoff: float = 2.0,
        max_delay: float = 60.0,
        jitter: bool = True,
        retry_on: type[Exception] | tuple[type[Exception], ...] = Exception,
        raise_args: Iterable[Any] | None = None,
        raise_kwargs: Mapping[str, Any] | None = None,
        on_retry: RetryCallback | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        Decorator that retries a function on failure with exponential backoff.

        Args:
            message:          Message for final exception. Supports {attempts} placeholder.
            max_attempts:     Maximum number of attempts (including initial attempt). Must be >= 1.
            backoff:          Exponential backoff multiplier. Delay = backoff^attempt.
            max_delay:        Maximum delay between retries in seconds.
            jitter:           Add random jitter to prevent thundering herd.
            retry_on:         Exception type(s) to retry. Other exceptions will be raised immediately.
            raise_args:       Additional positional args for the raised exception.
            raise_kwargs:     Keyword args for the raised exception.
            on_retry:         Optional callback invoked on each retry with (attempt, exception).

        Returns:
            Decorated function that retries on failure.

        Example:
            @Buzz.retry("Failed to fetch data after {attempts} attempts", max_attempts=3, backoff=2.0, retry_on=(ConnectionError, TimeoutError))
            def fetch_data(url):
                response = requests.get(url)
                response.raise_for_status()
                return response.json()
        """
        return retry(
            message=message,
            max_attempts=max_attempts,
            backoff=backoff,
            max_delay=max_delay,
            jitter=jitter,
            retry_on=retry_on,
            raise_exc_class=cls,
            raise_args=raise_args,
            raise_kwargs=raise_kwargs,
            exc_builder=cls.exc_builder,
            on_retry=on_retry,
        )

    @classmethod
    def retry_async(
        cls,
        message: str,
        max_attempts: int = 3,
        backoff: float = 2.0,
        max_delay: float = 60.0,
        jitter: bool = True,
        retry_on: type[Exception] | tuple[type[Exception], ...] = Exception,
        raise_args: Iterable[Any] | None = None,
        raise_kwargs: Mapping[str, Any] | None = None,
        on_retry: RetryCallback | None = None,
    ) -> Callable[[Callable[..., Coroutine[Any, Any, Any]]], Callable[..., Coroutine[Any, Any, Any]]]:
        """
        Decorator that retries an async function on failure with exponential backoff.

        Args:
            message:          Message for final exception. Supports {attempts} placeholder.
            max_attempts:     Maximum number of attempts (including initial attempt). Must be >= 1.
            backoff:          Exponential backoff multiplier. Delay = backoff^attempt.
            max_delay:        Maximum delay between retries in seconds.
            jitter:           Add random jitter to prevent thundering herd.
            retry_on:         Exception type(s) to retry. Other exceptions will be raised immediately.
            raise_args:       Additional positional args for the raised exception.
            raise_kwargs:     Keyword args for the raised exception.
            on_retry:         Optional callback invoked on each retry with (attempt, exception).

        Returns:
            Decorated async function that retries on failure.

        Example:
            @Buzz.retry_async("Failed to fetch data after {attempts} attempts", max_attempts=3, backoff=2.0, retry_on=(ConnectionError, TimeoutError))
            async def fetch_data(url):
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        return await response.json()
        """
        return retry_async(
            message=message,
            max_attempts=max_attempts,
            backoff=backoff,
            max_delay=max_delay,
            jitter=jitter,
            retry_on=retry_on,
            raise_exc_class=cls,
            raise_args=raise_args,
            raise_kwargs=raise_kwargs,
            exc_builder=cls.exc_builder,
            on_retry=on_retry,
        )
