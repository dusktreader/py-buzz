[![PyPI version][pypi-badge]][pypi-project]
[![Python versions][python-badge]][python-versions]
[![Build status][build-badge]][build-workflow]
[![Documentation status][docs-badge]][docs-site]

![py-buzz-logo](https://github.com/dusktreader/py-buzz/blob/main/docs/source/images/buzz-logo-text.png)

**That's not flying, _it's falling with style_: Exceptions with extras**

![py-buzz-demo](https://github.com/dusktreader/py-buzz/blob/main/docs/source/images/py-buzz.gif)

Long ago, I found myself writing the same boilerplate for condition checks and exception wrappers over and over. So I
gathered some helpers together to cut down on repetitive error-handling code. When I switched projects later, I wanted
those helpers there, too! That's how `py-buzz` came to be.

Now, I have a collection of really useful exception helpers that I can use in all my projects, and I'm sharing them with
you!


## Getting started

Python 3.11 or newer is required, and installation takes one line:

```shell
uv add py-buzz
```

Here's a small example with a project-specific exception:

```python
from buzz import Buzz


class ConfigError(Buzz):
    pass


def read_port(value: object) -> int:
    port = ConfigError.ensure_type(value, int, "Port must be an integer")
    ConfigError.require_condition(1 <= port <= 65535, "Port must be between 1 and 65535")
    return port


def parse_port(value: str) -> int:
    with ConfigError.handle_errors("Couldn't parse the configured port"):
        port = int(value)
    return read_port(port)
```

Here, `ensure_type()` checks the value at runtime and returns it with a narrowed type, while `require_condition()`
raises `ConfigError` if the port is out of range. `handle_errors()` gives parsing failures
a bit more context by wrapping the original `ValueError` in a `ConfigError`.


## What's in the box

- Checks for conditions, defined values, types, and `Literal` values, with useful errors.
- More context around handled exceptions, or a new exception raised from the original.
- Several failed checks gathered into one report.
- Synchronous and asynchronous retries with exponential backoff through `Buzz.retry()` and `Buzz.retry_async()`.
- A `Buzz` base class for project-specific exceptions, along with standalone helpers for existing exception types.


## Further reading

The [documentation](https://dusktreader.github.io/py-buzz/) has feature guides and the API reference.

A set of demos is also included if you want to see the features in action. You can run them with one line:

```shell
uvx --from='py-buzz[demo]' py-buzz-demo
```

[pypi-badge]: https://img.shields.io/pypi/v/py-buzz?label=pypi-version&logo=python&style=plastic
[pypi-project]: https://pypi.org/project/py-buzz/
[python-badge]: https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fdusktreader%2Fpy-buzz%2Fmain%2Fpyproject.toml&style=plastic&logo=python&label=python-versions
[python-versions]: https://www.python.org/
[build-badge]: https://github.com/dusktreader/py-buzz/actions/workflows/main.yml/badge.svg
[build-workflow]: https://github.com/dusktreader/py-buzz/actions/workflows/main.yml
[docs-badge]: https://github.com/dusktreader/py-buzz/actions/workflows/docs.yml/badge.svg
[docs-site]: https://dusktreader.github.io/py-buzz/
