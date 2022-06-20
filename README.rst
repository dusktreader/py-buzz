.. image::  https://badge.fury.io/py/py-buzz.svg
   :target: https://badge.fury.io/py/py-buzz
   :alt:    Latest Version

.. image::  https://travis-ci.org/dusktreader/py-buzz.svg?branch=integration
   :target: https://travis-ci.org/dusktreader/py-buzz
   :alt:    Build Status

.. image::  https://readthedocs.org/projects/py-buzz/badge/?version=latest
   :target: http://py-buzz.readthedocs.io/en/latest/?badge=latest
   :alt:    Documentation Status

*********
 py-buzz
*********

------------------------------------------------------------------
That's not flying, it's falling with style: Exceptions with extras
------------------------------------------------------------------

py-buzz supplies some useful tools to use with python exceptions as well
as a base Buzz exception class that includes them as classmethods.

py-buzz is fully equipped with exception tools that are written over and over
again in python projects such as:

* checking conditions and raising errors on failure (``require_conditon``)
* checking that values are defined and raising errors if not (``enforce_defined``)
* catching exceptions wrapping them in clearer exception types with better error
  messages (``handle_errors``)
* checking many conditions and reporting which ones failed
  (``check_expressions``)

Buzz can be used as a stand-alone exception class, but it is best used as a
bass class for custom exceptions within a project. This allows the user to
focus on creating a set of Exceptions that provide complete coverage for issues
within their application without having to re-write convenience functions
themselves.

Super-quick Start
-----------------
 - requirements: `python3.6+`
 - install through pip: `$ pip install py-buzz`
 - minimal usage example: `examples/with_buzz_class.py <https://github.com/dusktreader/py-buzz/tree/master/examples/with_buzz_class.py>`_

Documentation
-------------

The complete documentation can be found at the
`py-buzz home page <http://py-buzz.readthedocs.io>`_
