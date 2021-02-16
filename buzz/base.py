import contextlib
import inspect
import os
import sys
import textwrap

import deprecated
import inflection


class Buzz(Exception):
    """
    This provides a specialized exception class. It has some shiny features
    like:
      * require_condition: asserts a condition and raises an exception otherwise
      * handle_errors:     a context manager that handles exceptions
      * check_expressions: a context manager that checks multiple expressions
    """

    def __init__(self, message):
        """
        Initializes the exception

        :param: message:    The failure message to attach to the raised Buzz
        """
        self.message = textwrap.dedent(message).strip()

    def __str__(self):
        return self.message

    def __repr__(self):
        return self.__class__.__name__

    @classmethod
    @contextlib.contextmanager
    def check_expressions(cls, main_message, *init_args, **init_kwargs):
        """
        Checks a series of expressions inside of a context manager. Each is
        checked, and if any fail an exception is raised that contains a main
        message and a description of each failing expression:

        .. code-block:: python
        with Buzz.check_expressions("Something wasn't right") as check:
            check(a is not None)
            check(a > b, "a must be greater than b")
            check(a != 1, "a must not equal 1")
            check(b >= 0, "b must not be negative")

        This would render output like:
        .. code-block:: bash

        Checked expressions failed: Something wasn't right:
          1: first expressoin failed
          3: a must not equal 1

        Passes along inititalization args if triggered
        """

        class _Checker:
            def __init__(self):
                self.problems = []
                self.expression_counter = 0

            def check(self, evaluated_expression, message=None):
                self.expression_counter += 1
                if not evaluated_expression:
                    if message is None:
                        message = "{nth} expression failed".format(
                            nth=inflection.ordinalize(self.expression_counter),
                        )
                    self.problems.append(
                        "{i}: {msg}".format(
                            i=self.expression_counter,
                            msg=message,
                        )
                    )

        checker = _Checker()
        yield checker.check
        cls.require_condition(
            len(checker.problems) == 0,
            "Checked expressions failed: {}\n  {}".format(
                main_message,
                "\n  ".join(checker.problems),
            ),
            *init_args,
            **init_kwargs,
        )

    @classmethod
    def reformat_exception(cls, message, err):
        """
        Reformats an exception by adding a message to it and reporting the
        original exception name and message
        """
        final_message = "{} -- {}: {}".format(
            message,
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
        cls,
        message,
        *init_args,
        re_raise=True,
        exception_class=Exception,
        do_finally=None,
        do_except=None,
        do_else=None,
        **init_kwargs,
    ):
        """
        provides a context manager that will intercept exceptions and repackage
        them as Buzz instances with a message attached:

        .. code-block:: python
        with Buzz.handle_errors("It didn't work"):
            some_code_that_might_raise_an_exception()

        :param: message:         The message to attach to the raised Buzz
        :param: *init_args:      Additional positional args that should be passed
                                 to init in the event of an exception. Will be
                                 used for re-raised exception
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
        :param: **init_kwargs:   Additional keyword args that should be passed
                                 to init in the event of an exception. Will be
                                 used for re-raised exception
        """
        try:
            yield
        except exception_class as err:
            try:
                final_message = cls.reformat_exception(message, err)
            except Exception as msg_err:
                raise cls("Failed while formatting message: {}".format(repr(msg_err)))

            trace = cls.get_traceback()

            if do_except is not None:
                do_except(err, final_message, trace)
            if re_raise:
                raise cls(final_message, *init_args, **init_kwargs).with_traceback(trace)
        else:
            if do_else is not None:
                do_else()
        finally:
            if do_finally is not None:
                do_finally()

    @classmethod
    def require_condition(cls, expr, message, *init_args, **init_kwargs):
        """
        used to assert a certain state. If the expression renders a false
        value, an exception will be raised with the supplied message

        :param: message:       The failure message to attach to the raised Buzz
        :param: expr:          A boolean value indicating an evaluated expression
        :param: **init_args:   Additional positional args that should be passed
                               to init in the event of a failed expression. Will
                               be used to initialize the raised exception.
        :param: **init_kwargs: Additional keyword args that should be passed
                               to init in the event of a failed expression. Will
                               be used to initialize the raised exception.
        """
        if not expr:
            raise cls(message, *init_args, **init_kwargs)

    @classmethod
    def sanitize_errstr(cls, err):
        """
        Replaces curly braces in the string representation of an exception so
        that string formatting does not attempt to replace the fields with
        format values

        :param errstr: The string to sanitize
                       This is typically aquired from a caught error
        """
        return str(err)
        # return str(err).replace("{", "{{").replace("}", "}}")
