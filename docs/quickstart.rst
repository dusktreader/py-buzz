Quickstart
==========

Requirements
------------

* Python 3.7 or greater

Installation
------------

Install from pypi
.................

This will install the latest release of py-buzz from pypi via pip::

$ pip install py-buzz


Using
-----

Just import!

.. code-block:: python

   from buzz import require_condition

   require_condition(check_something(), "The check failed!")
