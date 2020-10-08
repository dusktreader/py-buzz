Features
========

Main Features
-------------
There are 3 main features of Buzz that are noteworthy:

Raise exception on condition failure
....................................
Buzz provides a function that checks a condition and raises an exception if
it fails. This is nice, because you often find your self writing a lot of
``if <whatever>: raise Exception(<message>)`` throughout your code base. Buzz
makes it just a little easier to write and read that kind of code:

.. code-block:: python

   # Vanilla python
   if not some_condition():
       raise Exception("some_condition failed")

   # With py-buzz
   Buzz.require_condition(some_condition(), "some_condition failed")

This is again justa bit of syntactic sugar but can make code a bit more
palletable, especially if you have to check a lot of invariants in a function

Exception handling context manager
..................................
Buzz also provides a context manager that catches any exceptions that might
be caught in executing a bit of code. The caught exceptions are re-packaged as
Buzz errors and re-raised with a message that captures the initial exception's
message:

.. code-block:: python

   # Vanilla python
   try:
      this_could_fail()
      this_could_also_fail()
      this_will_definitely_fail()
   except Exception as err:
       raise Exception("Something didn't work -- Error: {}".format(str(err)))

   # With py-buzz
   with Buzz.handle_errors("Something didn't work"):
      this_could_fail()
      this_could_also_fail()
      this_will_definitely_fail()

This actually can save a bit of code and makes things a bit cleaner. It is also
a pattern that tends to get repeated over and over again. If more complex
error handling logic is needed, this context manager shouldn't be used. It is
intended to just handle simple re-packaging of exceptions in a block of code

More about Main Features
------------------------

There are some additional behaviors of the main features that warrant disussion

handle_errors()
...............

The ``handle_errors()`` method has a lot of functionality that can be very
useful. These extra functions are supplied in the additional arguments to
the context manager:

exception_class
```````````````

This option describes the type of exception that will be handled by this context
manager. Any instance of the option's excepion (or any of it's derived exception
classes) will be caught. This is very useful if you only want to handle a
certain category of exceptions and let the others rise up un-altered:

.. code-block:: python

   with Buzz.handle_errors(
       "Something went wrong",
       exception_class=MyProjectError,
   ):
       some_function_that_could_mine_or_other_errors()

Exception instances that do not fall within the inheritance tree of the
exception_class option will not be handled at all. It is worth noting that the
``do_except`` task will not be executed if an other exception occurs. However,
the ``do_else`` and ``do_finally`` tasks will be executed normally.

do_except
`````````

Often, it is useful to do some particular things when an exception is caught.
Most frequently this includes logging the exception. The ``do_except`` optional
argument provides the ability to do this. The ``do_finally`` option should be a
callable function that accepts 3 parameters::

* The caught exception itself
* A message describing the error (This will be the formatted error message)
* A stack trace

This option might be invoked something like this:

.. code-block:: python

   def log_error(err, message, trace):
       logger.error(message)
       logger.error('\n'.join(trace))

   with Buzz.handle_errors("Somethign went wrong", do_except=log_error):
       some_dangerous_function()

do_else
```````

This option describes some action that should happen if no exceptions are
encountered. This option is less useful than ``do_except`` but it may useful in
some circumstances. This option should be a callable that takes no arguments:

.. code-block:: python

   def log_yay():
       logger.info("we did it!")

   with Buzz.handle_errors("Something went wrong", do_else=log_yay):
       some_not_dangerous_function()

do_finally
``````````

This option describes some action that should happen whether at the end of the
context regardless to whether an exception occurred or not. This is a useful
feature if you need to do some cleanup in either case. It should take a callable
that receives no arguments:

.. code-block:: python

   def close_resource():
       resource.close()

   with Buzz.handle_errors("Something went wrong", do_finally=close_resource):
       some_dangerous_function_that_uses_resource(resource)


re_raise
````````

The ``re_raise`` argument is set to ``True`` by default. This means that any
exceptions that are caught in the handler will be wrapped in a Buzz exception
and then that exception will be raised. Sometimes, you want your error handler
to do some work and then absorb the exceptions. In this case, you should set the
``re_raise`` option to ``False``. In this case, the exception will not be
raised. Any additional actions provided by ``do_finally``, ``do_except``, and
``do_else`` will still be executed.


Additional Features
-------------------

check_expressions
.................

The ``check_expressions`` context manager is used to check multiple expressions
inside of a context manager. Each expression is checked and each failing
expression is reported at the end in a raised exception. If no expressions fail
in the block, no exception is raised.

.. code-block:: python

    with pytest.raises(Buzz) as err_info:
        with Buzz.check_expressions(
                main_message='there will be errors',
        ) as check:
            check(True)
            check(False)
            check(1 == 2, "one is not two")
            check('cooooooool', 'not a problem')
            check(0, "zero is still zero")

If the above code was executed, an exception would
be raised that looks like this::

   Buzz: Checked expressions failed: there will be errors
     2: 2nd expression failed
     3: one is not two
     5: zero is still zero


reformat_exception
..................

This method is used internally by the ``handle_errors`` context manager.
However, it is sometimes useful in other circumstances. It simply allows you to
wrap an exception message in a more informative block of text:

.. code-block:: python

   try:
       raise ValueError("I didn't like that")
   except Exception as err:
       print(buzz.Buzz.reformat_exception("welp...that didn't work", err))

The above block would result in output like::

> welp...that didn't work -- ValueError: I didn't like that

get_traceback
`````````````

This function is just a tool to fetch the traceback for the current function. It
does this by fetching it out of ``sys.exc_info``. It is used internally with
Buzz but could be useful in other contexts
