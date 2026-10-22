# Check multiple expressions

The `check_expressions()` context manager gathers the results of multiple checks in a block. Any failures appear
together in one exception at the end; when every check passes, no exception is raised.


## Basic use

```python {linenums="1"}
from buzz import check_expressions

with check_expressions("there will be errors") as check:
    check(True)
    check(False)
    check(1 == 2, "one is not two")
    check('cooooooool', 'not a problem')
    check(0, "zero is still zero")
```

The example raises an exception like this:

```text
Exception: Checked expressions failed: there will be errors
   2: 2nd expression failed
   3: one is not two
   5: zero is still zero
```

A `Buzz` subclass method uses the same checks and raises that subclass:

```python {linenums="1"}
from buzz import Buzz

class ConfigError(Buzz):
    pass

with ConfigError.check_expressions("there will be errors") as check:
    check(False, "configuration is invalid")
```


## Advanced use

The standalone `check_expressions()` function lets you customize how the combined failure is constructed. The builder
receives `base_message` as well as the assembled message and constructor
arguments, and must forward those fields to the exception constructor:

```python {linenums="1"}
from buzz import Buzz, check_expressions
from buzz.tools import ExcBuilderParams


class ValidationError(Exception):
    def __init__(self, message: str, phase: str, *, source: str, base_message: str):
        self.phase = phase
        self.source = source
        self.base_message = base_message
        super().__init__(message)


def build_validation_error(params: ExcBuilderParams) -> Exception:
    return params.raise_exc_class(
        params.message,
        *params.raise_args,
        base_message=params.base_message,
        **params.raise_kwargs,
    )


def report_failure(exc: Exception) -> None:
    print(f"Validation failed: {exc}")


def report_success() -> None:
    print("Configuration passed validation")


def validate_config(config: object) -> None:
    with check_expressions(
        "Invalid configuration",
        raise_exc_class=ValidationError,
        raise_args=["startup"],
        raise_kwargs={"source": "environment"},
        exc_builder=build_validation_error,
        do_except=report_failure,
        do_else=report_success,
    ) as check:
        check(hasattr(config, "host"), "host is required")
        check(getattr(config, "port", 0) > 0, "port must be positive")
```

Here `do_except` receives the constructed exception itself, not a `DoExceptParams` object. The first failed expression
or both checks failing produces one `ValidationError`, with `phase="startup"`, `source="environment"`, and the
`"Invalid configuration"` base message. If every check passes, `do_else` runs instead.

A `Buzz` subclass method binds its own exception class and builder,
so it does not accept `raise_exc_class` or `exc_builder`:

```python {linenums="1"}
class ValidationBuzzError(Buzz):
    def __init__(self, message: str, phase: str, *, source: str, base_message: str | None = None):
        self.phase = phase
        self.source = source
        super().__init__(message, base_message=base_message)


with ValidationBuzzError.check_expressions(
    "Invalid configuration",
    raise_args=["startup"],
    raise_kwargs={"source": "environment"},
    do_except=report_failure,
    do_else=report_success,
) as check:
    check(hasattr(config, "host"), "host is required")
    check(getattr(config, "port", 0) > 0, "port must be positive")
```

The context manager evaluates checks synchronously as they are called.
