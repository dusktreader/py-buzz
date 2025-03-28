[![Latest Version](https://img.shields.io/pypi/v/py-buzz?label=pypi-version&logo=python&style=plastic)](https://pypi.org/project/py-buzz/)
[![Python Versions](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fdusktreader%2Fpy-buzz%2Fmain%2Fpyproject.toml&style=plastic&logo=python&label=python-versions)](https://www.python.org/)
[![Build Status](https://github.com/dusktreader/py-buzz/actions/workflows/main.yml/badge.svg)](https://github.com/dusktreader/py-buzz/actions/workflows/main.yml)
[![Documentation Status](https://github.com/dusktreader/py-buzz/actions/workflows/docs.yml/badge.svg)](https://dusktreader.github.io/py-buzz/)

![py-buzz-logo](https://github.com/dusktreader/py-buzz/blob/main/docs/source/images/buzz-logo-text.png)

**That's not flying, _it's falling with style_: Exceptions with extras**

![asciicast](https://github.com/dusktreader/py-buzz/blob/main/docs/source/images/py-buzz.gif)

py-buzz is fully equipped with a suite of exception tools that will save you
from writing the same code over and over again in your python projects. These
include:

* checking many conditions and reporting which ones failed (`check_expressions()`)
* catching exceptions wrapping them in clearer exception types with better error messages (`handle_errors()`)
* checking that values are defined and raising errors if not (`enforce_defined()`)
* checking conditions and raising errors on failure (`require_condition()`)

py-buzz also provides an exception class, Buzz, that can be used  as a base class
for custom exceptions within a project.

## Super-quick Start

* Only requires Python 3.9 or later
* Installed with pip (`$ pip install py-buzz`)
* Each feature demonstrated in an executable demo "extra"

## Documentation

The complete documentation can be found at the [py-buzz documentation page](https://dusktreader.github.io/py-buzz/)
