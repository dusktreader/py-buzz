import textwrap

from buzz.tools import check_expressions, get_traceback, handle_errors, require_condition


class Buzz(Exception):
    """
    This provides a specialized exception class that wraps up all the buzz utility functions.
    """

    def __init__(self, message):
        """
        Initialize the exception with a message. Dedent the supplied message.
        """
        self.message = textwrap.dedent(message).strip()

    def __str__(self):
        return self.message

    def __repr__(self):
        return self.__class__.__name__

    @classmethod
    def require_condition(cls, *args, **kwargs):
        """
        Call the require_condition function with this class as the ``raise_exc_class`` kwarg.
        """
        if "raise_exc_class" in kwargs:
            raise ValueError("You may not pass the 'raise_exc_class' to Buzz-derived exception methods")
        return require_condition(*args, raise_exc_class=cls, **kwargs)

    @classmethod
    def check_expressions(cls, *args, **kwargs):
        """
        Call the check_expressions context manager with this class as the ``raise_exc_class`` kwarg.
        """
        if "raise_exc_class" in kwargs:
            raise ValueError("You may not pass the 'raise_exc_class' to Buzz-derived exception methods")
        return check_expressions(*args, raise_exc_class=cls, **kwargs)

    @classmethod
    def handle_errors(cls, *args, re_raise=True, **kwargs):
        """
        Call the handle_errors context manager with this class as the ``raise_exc_class`` kwarg.
        If ``re_raise`` is not True, ``None`` will be passed as the ``raise_exc_class`` kwarg.
        """
        if "raise_exc_class" in kwargs:
            raise ValueError("You may not pass the 'raise_exc_class' to Buzz-derived exception methods")
        return handle_errors(*args, raise_exc_class=cls if re_raise else None, **kwargs)

    @classmethod
    def get_traceback(cls, *args, **kwargs):
        """
        Call the get_traceback function.
        """
        return get_traceback(*args, **kwargs)
