"""
This module defines the Buzz base class.
"""

from __future__ import annotations

import sys
import textwrap
from typing import TypeVar, Any
if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

from buzz import tools

TNonNull = TypeVar("TNonNull")


class Buzz(Exception):
    """
    This provides a specialized exception class that wraps up all the buzz utility functions.
    """

    def __init__(self, message: str):
        """
        Initialize the exception with a message.

        Also, dedent the supplied message.
        """

        self.message: str = textwrap.dedent(message).strip()
        super().__init__(self.message)

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
    def require_condition(cls, *args: Any, **kwargs: Any):
        """
        Call the `require_condition()` function with this class as the `raise_exc_class` kwarg.
        """
        cls._check_kwargs(**kwargs)
        # Type checking ignored  because https://github.com/python/mypy/issues/6799
        return tools.require_condition(*args, raise_exc_class=cls, **kwargs) # type: ignore

    @classmethod
    def enforce_defined(cls, value: TNonNull | None, *args: Any, **kwargs: Any) -> TNonNull:
        """
        Call the `enforce_defined()` function with this class as the `raise_exc_class` kwarg.
        """
        cls._check_kwargs(**kwargs)
        # Type checking ignored  because https://github.com/python/mypy/issues/6799
        return tools.enforce_defined(value, *args, raise_exc_class=cls, **kwargs) # type: ignore

    @classmethod
    def check_expressions(cls, *args: Any, **kwargs: Any):
        """
        Call the `check_expressions()` context manager with this class as the `raise_exc_class` kwarg.
        """
        cls._check_kwargs(**kwargs)
        # Type checking ignored  because https://github.com/python/mypy/issues/6799
        return tools.check_expressions(*args, raise_exc_class=cls, **kwargs) # type: ignore

    @classmethod
    def handle_errors(cls, *args: Any, re_raise: bool = True, **kwargs: Any):
        """
        Call the `handle_errors()` context manager with this class as the `raise_exc_class` kwarg.

        Note:

            If `re_raise` is not True, `None` will be passed as the `raise_exc_class` kwarg.
        """
        cls._check_kwargs(**kwargs)
        # Type checking ignored  because https://github.com/python/mypy/issues/6799
        return tools.handle_errors(*args, raise_exc_class=cls if re_raise else None, **kwargs) # type: ignore

    @classmethod
    def get_traceback(cls, *args: Any, **kwargs: Any):
        """
        Call the `get_traceback()` function.
        """
        return tools.get_traceback(*args, **kwargs)
