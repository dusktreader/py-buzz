Quickstart
==========

Requirements
------------

* Python 3.4 or greater

Note on Requirements
....................

There are not currently plans to support python 2. It might be a nice-to-have,
but there are enough other features to work on at the moment.
Additionally, the original author is a proponent of python 3 adoption.

Installation
------------

Install from pypi
.................
This will install the latest release of py-buzz from pypi via pip::

$ pip install py-buzz

Install latest version from github
..................................
If you would like a version other than the latest published on pypi, you may
do so by cloning the git repostiory::

$ git clone https://github.com/dusktreader/py-buzz.git

Next, checkout the branch or tag that you wish to use::

$ cd py-buzz
$ git checkout integration

Finally, use pip to install from the local directory::

$ pip install .

.. note::

   py-buzz setup is not tested with distutils or setuptools. pip is a really
   complete package manager and has become the de-facto standard for installing
   python packages from remote locations. Compatability with pip is of primary
   importance, and since pip is such a great tool, it makes the most sense to
   the original author to use pip for local installs as well.

Using
-----
Just import!

.. code-block:: python

   from buzz import Buzz
   raise Buzz("something went wrong!")

Buzz also makes an excellent base-class for your project specific exception
classes!
