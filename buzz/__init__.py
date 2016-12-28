import contextlib
import inspect
import os
import textwrap


class Buzz(Exception):
    """
    This provides a specialized exception class. It has some shiny features
    like the ability to automatically substitute format args and kwargs into
    the supplied message. There is also a helper function called
    require_condition that can be used to assert a certain state and upon
    failure raise an exception
    """

    @classmethod
    @contextlib.contextmanager
    def accumulate_errors(cls, message, *format_args, **format_kwargs):

        class Accumulator:

            def __init__(self):
                self.problems = []
                self.msg = (
                    '{file}[{line}]->{func}(): '
                    '`{code}` resolved as false'
                )

            def __iadd__(self, evaluated_expression):
                if not evaluated_expression:
                    calling_frame = inspect.currentframe().f_back
                    traceback = inspect.getframeinfo(calling_frame)
                    self.problems.append(self.msg.format(
                        file=os.path.basename(traceback.filename),
                        func=traceback.function,
                        line=traceback.lineno,
                        code=traceback.code_context[0].strip(),
                    ))
                return self

        accumulator = Accumulator()
        yield accumulator
        cls.require_condition(
            len(accumulator.problems) == 0,
            "Checked condition(s) failed: {}\n{}",
            message.format(*format_args, **format_kwargs),
            '\n'.join(accumulator.problems),
            )

    @classmethod
    @contextlib.contextmanager
    def handle_errors(
            cls, message, *format_args,
            do_finally=None, on_error=None, **format_kwds
    ):
        """
        provides a context manager that will intercept exceptions and repackage
        them as Buzz instances with a message attached:

        .. code-block:: python
        with Buzz.handle_errors("It didn't work"):
            some_code_that_might_raise_an_exception()

        :param: message:    The failure message to attach to the raised Buzz
        :param format_args: Format arguments. Follows str.format convention
        :param format_kwds: Format keyword args. Follows str.format convetion
        :param do_finally:  A function that should always be called at the
                            end of the block. Should take no parameters
        :param on_error:    A function that should be called only if there was
                            an exception. Should take the raised exception as
                            its first parameter and the final message for the
                            exception that will be raised as its second
        """
        try:
            yield
        except Exception as err:
            final_message = message.format(*format_args, **format_kwds)
            final_message = "{} -- Error: {}".format(final_message, str(err))
            final_message = cls.sanitize_errstr(final_message)
            if on_error is not None:
                on_error(err, final_message)
            raise cls(final_message)
        finally:
            if do_finally is not None:
                do_finally()

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
        self.message = textwrap.dedent(
            message.format(*format_args, **format_kwds)
        ).strip()

    def __str__(self):
        return self.message

    def __repr__(self):
        return self.__class__.__name__
