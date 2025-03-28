# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## v7.0.0 - 2025-03-28
* Removed `exc_builder` option from `Buzz`
* Added `exc_builder` classmethod for `Buzz`
* Added rich demo
* Added demo page to docs
* Removed examples folder (see `src/demo` instead)
* Updated the README
* Minor docs updates
* Updated tests


## v6.1.0 - 2025-03-27
* Added `base_message` to `ExcBuilderParams`
* Improved typing
* Improved function signatures and docstrings in base.py
* Added basedpyright to type checking
* Added and updated unit tests.

## v6.0.3 - 2025-03-24
* Restored py.typed that was accidentally excluded

## v6.0.2 - 2025-03-24
* Fixed badges in README.md

## v6.0.1 - 2025-03-24
* Fixed wrong version (3.8) mention in README.md
* Fixed wrong version (3.8) mention in docs

## v6.0.0 - 2025-03-21
* Converted to a uv project
* Fixed typing issues

## v5.0.2 - 2025-01-29
* Update docstrings and docs for `handle_errors_async`

## v5.0.1 - 2025-01-29
* Added `handle_errors_async` to exported list from base package

## v5.0.0 - 2025-01-29
* Dropped support for Python 3.8
* Updated some dependencies
* Added `handle_errors_async`

## v4.2.0 - 2024-10-08

* Added `base_message` option to `DoExceptParams`.
* Changed `exc_builder` option to expect a new `ExcBuilderParams` class.
* Updated documentation.

## v4.1.0 - 2022-08-31

* Added `ignore_exc_class` option to `handle_errors`.

## v4.0.0 - 2022-07-30

* Dropped support for Python 3.6 and Python 3.7
* Upgraded dev dependencies including Pytest 7
* Converted documentation to markdown


## v3.3.0 - 2022-06-20

* Added `exc_builder` option to all methods.


## v3.2.1 - 2022-06-20

* Added `enforce_defined()` to Buzz class.

## v3.2.0 - 2022-06-20

* Added `enforce_defined()` function with tests and docs.


## v3.1.1 - 2022-04-05

* Added `raise from` in handle_errors (how did I miss this for so long?)


## v3.1.0 - 2022-03-23

* Returned support for Python 3.6


## v3.0.0 - 2022-01-15

* Moved functions to standalone tools module
* Made Buzz re-use these methods
* Changed `handle_errors` `exception_class` parameter to `handle_exc_class`
* Changed `handle_errors` to send `DoExceptParams` as a single parameter
* Removed `sanitize_err_string` as it should not be needed after 2.0.0
* Removed `re_raise` parameter from handle_errors in tools.
* Made passing `None` to raise_exc_class indicate no new excepton should be raised
* Added a Makefile for running quality checks easier.
* Updated and added examples.
* Updated docs a lot.
* Dropped support for Python 3.6


## v2.1.1-3 - 2021-02-16

* Fixed args in check_expressions


## v2.1.0 - 2021-02-10

* Added ability to forward init args for derived classes


## v2.0.0 - 2020-10-08

* Dropped support for python 3.5
* Removed deprecated features (format args especially)
* Added black & isort pre-commit hooks
* Updated examples and doucmentation
* Updated inflection dependency version

## v1.0.3 - 2019-06-05

* Added tests for use of handle_errors as a decorator
* Added deprecation warnings for removal of format args, kwargs


## v1.0.2 - 2019-05-13

* Updated README
* Updated examples
* Updated quickstart docs


## v1.0.1 - 2019-05-13

* Added readme to pyproject.toml


## v1.0.0 - 2019-05-13

* Deprecated accumulate errors (violated priniciple of least surprise)
* Added check_expressions as a more explicit multi-expression checker


## v0.4.0 - 2019-05-13

* Moved Buzz class code into base.py


## v0.3.7 - 2019-04-12

* Converted project to use poetry
* Added more documentation


## v0.3.5 - 2018-10-01

* Removed reformat_exception_with_traceback
* Added get_traceback. Simplicity is better


## v0.3.5 - 2018-10-01

* Added reformat_exception_with_traceback
* Added nox support


## v0.3.4 - 2018-05-09

* Fixed travis deploy collision issue


## v0.3.3 - 2018-02-22

* Updated long_description so pypi wouldn't fuck me over any more


## v0.3.2 - 2018-02-22

* Extracted reformat_exception method


## v0.3.1 - 2017-12-21

* Version bump because pypi is complaining about version conflicts

## v0.3.0 - 2017-12-21

* Added several examples to show features and complex behavior
* Added decals to README


## v0.2.0 - 2017-05-18

* Added documentation, hosted on readthedocs, and such


## v0.1.12 - 2017-05-17

* Added ability to handle only specific exceptions to handle_errors
* Improved exception reporting from within handle_errors


## v0.1.11 - 2017-04-19

* Added traceback to do_except


## v0.1.11 - 2017-04-19

* Added ability for handle_errors to absorb exception


## v0.1.9 - 2017-02-01

* Added traceback print out to handle_errors message
* Added exception class name to handle_errors output


## v0.1.8 - 2016-12-30

* Added formatted message string to on_error parameters
* Renamed project to 'py-buzz'
* Added error sanitization for messages with embedded curly braces


## v0.1.7 - 2016-12-22

* Fixed issues with packaging (took a lot of intermediary releases)
* Added accumulating context manager for checking expressions
* Added do_finally and on_error parameters to handle_errors
* Added repr function
* Added testing


## v0.1.0 - 2016-12-15

* First release of buzz-lightyear
* This CHANGELOG
* README providing a brief overview of the project
