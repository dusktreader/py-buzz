import contextlib
import inspect
import os
import sys
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
    def reformat_exception(cls, message, err, *format_args, **format_kwds):
        """
        Reformats an exception by adding a message to it and reporting the
        original exception name and message
        """
        final_message = message.format(*format_args, **format_kwds)
        final_message = "{} -- {}: {}".format(
            final_message,
            type(err).__name__,
            str(err),
        )
        final_message = cls.sanitize_errstr(final_message)
        return final_message

    @classmethod
    def get_traceback(cls):
        """
        This utility function just retrieves the traceback
        """
        return sys.exc_info()[2]

    @classmethod
    @contextlib.contextmanager
    def handle_errors(
            cls, message, *format_args,
            re_raise=True, exception_class=Exception,
            do_finally=None, do_except=None, do_else=None,
            **format_kwds
    ):
        """
        provides a context manager that will intercept exceptions and repackage
        them as Buzz instances with a message attached:

        .. code-block:: python
        with Buzz.handle_errors("It didn't work"):
            some_code_that_might_raise_an_exception()

        :param: message:         The message to attach to the raised Buzz
        :param: format_args:     Format arguments. Follows str.format conv.
        :param: format_kwds:     Format keyword args. Follows str.format conv.
        :param: re_raise:        If true, the re-packaged exception will be
                                 raised
        :param: exception_class: Limits the class of exceptions that will be
                                 re-packaged as a Buzz exception.
                                 Any other exception types will not be caught
                                 and re-packaged.
                                 Defaults to Exception (will handle all
                                 exceptions)
        :param: do_finally:      A function that should always be called at the
                                 end of the block. Should take no parameters
        :param: do_except:       A function that should be called only if there
                                 was an exception. Should take the raised
                                 exception as its first parameter, the final
                                 message for the exception that will be raised
                                 as its second, and the traceback as its third
        :param: do_else:         A function taht should be called only if there
                                 were no exceptions encountered
        """
        try:
            yield
        except exception_class as err:
            try:
                final_message = cls.reformat_exception(
                    message, err, *format_args, **format_kwds
                )
            except Exception as msg_err:
                raise cls(
                    "Failed while formatting message: {}".format(repr(msg_err))
                )

            trace = cls.get_traceback()

            if do_except is not None:
                do_except(err, final_message, trace)
            if re_raise:
                raise cls(final_message).with_traceback(trace)
        else:
            if do_else is not None:
                do_else()
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
