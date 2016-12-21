from contextlib import contextmanager
from textwrap import dedent


class Buzz(Exception):
    """
    This provides a specialized exception class. It has some shiny features
    like the ability to automatically substitute format args and kwargs into
    the supplied message. There is also a helper function called
    require_condition that can be used to assert a certain state and upon
    failure raise an exception
    """

    @classmethod
    @contextmanager
    def handle_errors(cls, message, *format_args, **format_kwds):
        """
        provides a context manager that will intercept exceptions and repackage
        them as Buzz instances with a message attached:

        .. code-block:: python
        with Buzz.handle_errors("It didn't work"):
            some_code_that_might_raise_an_exception()

        :param: message:    The failure message to attach to the raised Buzz
        :param format_args: Format arguments. Follows str.format convention
        :param format_kwds: Format keyword args. Follows str.format convetion
        """
        try:
            yield
        except Exception as err:
            raise cls(
                message + " -- Error: " + cls.sanitize_errstr(err),
                *format_args, **format_kwds
            )

    @classmethod
    def require_condition(cls, expr, message, *format_args, **format_kwds):
        """
        used to assert a certain state. If the expression renders a false
        value, an exception will be raised with the supplied message

        :param: message:    The failure message to attach to the raised Buzz
        :param: expr:       A boolean value indicating an evaluated expression
        :param format_args: Format arguments. Follows str.format convention
        :param format_kwds: Format keyword args. Follows str.format convetion
        """
        if not expr:
            raise cls(message, *format_args, **format_kwds)

    @classmethod
    def sanitize_errstr(cls, err):
        """
        Replaces curly braces in the string representation of an exception so
        that string formatting does not attempt to replace the fields with
        format values

        :param errstr: The string to sanitize
                       This is typically aquired from a caught error
        """
        return str(err).replace('{', '{{').replace('}', '}}')

    def __init__(self, message, *format_args, **format_kwds):
        """
        Initializes the exception

        :param: message:    The failure message to attach to the raised Buzz
        :param format_args: Format arguments. Follows str.format convention
        :param format_kwds: Format keyword args. Follows str.format convetion
        """
        self.message = dedent(
            message.format(*format_args, **format_kwds)
        ).strip()

    def __str__(self):
        return self.message

    def __repr__(self):
        return self.__class__.__name__
