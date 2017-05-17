Overview
========

This package supplies some extras to python exceptions that may be useful
within a python project. It is intended to supply some functionality that is
often written over and over again in packages. Most of the features are
relatively simple, but providing a consistent set of functionality is very
convenient when dealing with exceptions within your projects.

Buzz can be used as a stand-alone exception class, but it is best used as a
bass class for custom exceptions within a package. This allows the user to
focus on creating a set of Exceptions that provide complete coverage for issues
within their application without having to re-write convenience functions on
their base Exception class
