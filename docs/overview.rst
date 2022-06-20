Overview
========

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
