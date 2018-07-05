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

This package supplies some extras to python exceptions that may be useful
within a python project. It is intended to supply some functionality that is
often written over and over again in packages. Most of the features are
relatively simple, but providing a consistent set of functionality is very
convenient when dealing with exceptions within your projects.

Buzz can be used as a stand-alone exception class, but it is best used as a
base class for custom exceptions within a package. This allows the user to
focus on creating a set of Exceptions that provide complete coverage for issues
within their application without having to re-write convenience functions on
their base Exception class

Super-quick Start
-----------------
 - requirements: `python3`
 - install through pip: `$ pip install py-buzz`
 - minimal usage example: `examples/basic.py <https://github.com/dusktreader/py-buzz/tree/master/examples/basic.py>`_

Documentation
-------------

The complete documentation can be found at the
`py-buzz home page <http://py-buzz.readthedocs.io>`_
