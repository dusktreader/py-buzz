# py-buzz

![py-buzz-logo](images/buzz-logo-text.png)

**That's not flying, _it's falling with style_: Exceptions with extras**

![py-buzz-demo](images/py-buzz.gif)

Long ago, I found myself writing the same boilerplate for condition checks and exception wrappers over and over. So I
gathered some helpers together to cut down on repetitive error-handling code. When I switched
projects later, I wanted those helpers there, too! That's how `py-buzz` came to be.

Now, I have a collection of really useful exception helpers that
I can use in all my projects, and I'm sharing them with you!


## Getting started

Python 3.11 or newer is required, and installation takes one line:

```shell
uv add py-buzz
```

Here's a small example with a project-specific exception:

```python {linenums="1"}
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

Most helpers come in two flavors: standalone functions that work with regular exception types and methods on a `Buzz`
subclass that raise that class. `reformat_exception()` is a standalone helper for formatting exception messages.

- [`require_condition()`](features/require_condition.md) checks a condition.
- [`enforce_defined()`](features/enforce_defined.md) rejects `None` and narrows the value's type.
- [`ensure_type()`](features/ensure_type.md) checks a runtime type and narrows the result.
- [`verify_literal()`](features/verify_literal.md) checks a `Literal` value.
- [`handle_errors()` and `handle_errors_async()`](features/handle_errors.md) add context to exceptions from a block.
- [`Buzz.retry()` and `Buzz.retry_async()`](features/other_functions.md#retry-decorators)
  retry synchronous and asynchronous operations.
- [`check_expressions()`](features/check_expressions.md) reports multiple failed checks together.
- [`raise_from()`](features/raise_from.md) adds context while preserving the original exception as the cause.
- [`reformat_exception()`](features/other_functions.md#reformat-an-exception)
  formats an exception message with more context.
- [`get_traceback()`](features/other_functions.md#get-a-traceback) fetches the current traceback.

The standalone `retry()` and `retry_async()` decorators live in `buzz.tools`; the
[retry guide](features/other_functions.md#retry-decorators) shows both styles.


## The demos

The optional demo extra bundles executable examples of the features.
With `uv`, the demos can run in an isolated environment:

```shell
uvx --from='py-buzz[demo]' py-buzz-demo
```

The [demo guide](demo.md) has a few more ways to run individual examples.
