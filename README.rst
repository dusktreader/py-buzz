*********
 py-buzz
*********

------------------------------------------------------------------
That's not flying, it's falling with style: Exceptions with extras
------------------------------------------------------------------

This package is a light-weight extension of python's Exception class
with some added niceties

Requirements
============

 - Python 3

Installing
==========
Install using pip::

$ pip install py-buzz

Using
=====
Just import:

.. code-block:: python

   from buzz import Buzz
   raise Buzz("something went wrong!")

Buzz also makes an excellent base-class for your project specific exception
classes!

Features
========

Automatic message formatting
----------------------------
Buzz exception messages can be automatically formatted with format arguments
and keyword arguments. This saves a few characters and generally makes the
exception code a little easier to read:

.. code-block:: python

   # Vanilla python
   raise Exception("a {} message".format('formatted'))
   raise Exception("a {fmt} message".format(fmt='formatted'))

   # With py-buzz
   raise Buzz("a {} message", 'formatted')
   raise Buzz("a {fmt} message", fmt='formatted')

Obviously the benefits aren't that easy to see with a small message with few
args, but getting rid of an additional level of nesting can be nice with more
complex messages

Raise exception on condition failure
------------------------------------
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
----------------------------------
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
