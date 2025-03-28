"""
This module defines the Buzz base class.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
import textwrap
from typing import TypeVar, Any
from typing_extensions import Self, override

from buzz.tools import (
    DoExceptParams,
    ExcBuilderParams,
    noop,
    require_condition,
    enforce_defined,
    check_expressions,
    handle_errors,
    get_traceback,
)

TNonNull = TypeVar("TNonNull")


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

    @staticmethod
    def _check_kwargs(**kwargs: Any):
        """
        Ensure that `raise_exc_class()` was not passed as a keyword-argument.
        """
        if "raise_exc_class" in kwargs:
            raise ValueError("You may not pass the 'raise_exc_class' to Buzz-derived exception methods.")

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
    ):
        """
        Assert that an expression is truty. If the assertion fails, raise an exception (instance of this class) with the
        supplied message.

        Args:

            message:         The failure message to attach to the raised Exception
            expr:            The value that is checked for truthiness (usually an evaluated expression)
            raise_args:      Additional positional args (after the constructed message) that will passed when raising
                             an instance of the ``raise_exc_class``.
            raise_kwargs:    Keyword args that will be passed when raising an instance of the ``raise_exc_class``.
        """
        return require_condition(
            expr,
            message,
            raise_exc_class=cls,
            raise_args=raise_args,
            raise_kwargs=raise_kwargs,
            exc_builder=cls.exc_builder,
        )

    @classmethod
    def enforce_defined(
        cls,
        value: TNonNull | None,
        message: str = "Value was not defined (None)",
        raise_args: Iterable[Any] | None = None,
        raise_kwargs: Mapping[str, Any] | None = None,
    ) -> TNonNull:
        """
        Assert that a value is not None. If the assertion fails, raise an exception (instance of this class) with the
        supplied message.

        Args:

            value:            The value that is checked to be non-null
            message:          The failure message to attach to the raised Exception
            expr:             The value that is checked for truthiness (usually an evaluated expression)
            raise_args:       Additional positional args (after the constructed message) that will passed when raising
                              an instance of the ``raise_exc_class``.
            raise_kwargs:     Keyword args that will be passed when raising an instance of the ``raise_exc_class``.
        """
        return enforce_defined(
            value,
            message,
            raise_exc_class=cls,
            raise_args=raise_args,
            raise_kwargs=raise_kwargs,
            exc_builder=cls.exc_builder,
        )

    @classmethod
    def check_expressions(
        cls,
        base_message: str,
        raise_args: Iterable[Any] | None = None,
        raise_kwargs: Mapping[str, Any] | None = None,
    ):
        """
        Check a series of expressions inside of a context manager. If any fail an exception (instance of this class) is
        raised that contains a main message and a description of each failing expression.

        Args:
            base_message:      The base failure message to include in the constructed message that is passed to the
                               raised Exception. Will be included in `ExcBuilderParams` passed to `exc_builder`.
            raise_args:        Additional positional args (after the constructed message) that will passed when raising
                               an instance of the ``raise_exc_class``.
            raise_kwargs:      Keyword args that will be passed when raising an instance of the ``raise_exc_class``.

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
        )

    @classmethod
    def handle_errors(
        cls,
        base_message: str,
        re_raise: bool = True,
        raise_args: Iterable[Any] | None = None,
        raise_kwargs: Mapping[str, Any] | None = None,
        handle_exc_class: type[Exception] | tuple[type[Exception], ...] = Exception,
        ignore_exc_class: type[Exception] | tuple[type[Exception], ...] | None = None,
        do_finally: Callable[[], None] = noop,
        do_except: Callable[[DoExceptParams], None] = noop,
        do_else: Callable[[], None] = noop,
    ):
        """
        Provide a context manager that will intercept exceptions and repackage them in a new exception (instance of this
        class) with a message attached that combines the base message along with the message from the handled exception:

        Args:
            base_message:      The base message to attach to the raised exception. Will be included in `ExcBuilderParams`
                               passed to `exc_builder`.
            re_raise:          If True (the default), then a exception (instance of this class) will be raised after
                               handling any caught exceptoins. If False, no exception will be raised after handling any
                               exceptions. This will effectively swallow the expression. Note that the `do_` methods
                               will still be executed.
            raise_exc_class:   The exception type to raise with the constructed message if an exception is caught in the
                               managed context. If ``None`` is passed, no new exception will be raised and only the
                               ``do_except``, ``do_else``, and ``do_finally`` functions will be called.
            raise_args:        Additional positional args (after the constructed message) that will passed when raising
                               an instance of the ``raise_exc_class``.
            raise_kwargs:      Keyword args that will be passed when raising an instance of the ``raise_exc_class``.
            handle_exc_class:  Limits the class of exceptions that will be intercepted
                               Any other exception types will not be caught and re-packaged.
                               Defaults to Exception (will handle all exceptions). May also be provided as a tuple
                               of multiple exception types to handle.
            ignore_exc_class:  Defines an exception or set of exception types that should not be handled at all.
                               Any matching exception types will be immediately re-raised. They will not be handled by
                               the `handle_errors` context manager at all. This is useful if you want a specific variant
                               of your `handle_exc_class` to not be handled by `handle_errors`. For example, if you want
                               to use `handle_exc_class=Exception` but you do not want `handle_errors` to handle
                               `RuntimeError`.
                               Then, you would set `ignore_exc_class=RuntimeError`.
            do_finally:        A function that should always be called at the end of the block.
                               Should take no parameters.
            do_except:         A function that should be called only if there was an exception. Must accept one
                               parameter that is an instance of the ``DoExceptParams`` dataclass.
                               Note that the ``do_except`` method is passed the *original exception*.
            do_else:           A function that should be called only if there were no exceptions encountered.

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
    def get_traceback(cls, *args: Any, **kwargs: Any):
        """
        Call the `get_traceback()` function.
        """
        return get_traceback(*args, **kwargs)
