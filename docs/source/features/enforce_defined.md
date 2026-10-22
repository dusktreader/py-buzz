# Enforce a defined value

`enforce_defined()` checks that a value is not `None`, raising an exception otherwise. It also narrows the
value's type, which keeps static type checkers happy when you call a method on it.


## Basic use

```python {linenums="1"}
from buzz import enforce_defined

# Vanilla Python
def vanilla(val: str | None) -> str:
    if val is None:
        raise ValueError("Received an undefined value!")
    return val.upper()

# With py-buzz
def buzzy(val: str | None) -> str:
    return enforce_defined(val).upper()
```

When the value is `None`, `enforce_defined()` raises an exception with a simple default
message. A custom message is available through the `message` keyword argument.

A `Buzz` subclass method binds the exception type:

```python {linenums="1"}
from buzz import Buzz, enforce_defined

class ConfigError(Buzz):
    pass

value = enforce_defined(config_value, "Missing config value", raise_exc_class=ConfigError)
value = ConfigError.enforce_defined(config_value, "Missing config value")
```


## Advanced use

A custom exception can carry the identity and source of a missing value. The standalone function takes an explicit
non-Buzz exception class; the `Buzz` method binds its own class and exception
builder while still accepting constructor arguments and callbacks:

```python {linenums="1"}
from buzz import Buzz, enforce_defined


class MissingValueError(Exception):
    def __init__(self, message: str, field: str, *, source: str):
        self.field = field
        self.source = source
        super().__init__(message)


def report_missing(exc: Exception) -> None:
    print(f"Missing configuration: {exc}")


def report_present() -> None:
    print("Configuration value is present")


def read_database_url(value: str | None) -> str:
    return enforce_defined(
        value,
        "A database URL is required",
        raise_exc_class=MissingValueError,
        raise_args=["database_url"],
        raise_kwargs={"source": "environment"},
        do_except=report_missing,
        do_else=report_present,
    )


class MissingValueBuzzError(Buzz):
    def __init__(self, message: str, field: str, *, source: str, base_message: str | None = None):
        self.field = field
        self.source = source
        super().__init__(message, base_message=base_message)


def read_database_url_with_buzz(value: str | None) -> str:
    return MissingValueBuzzError.enforce_defined(
        value,
        "A database URL is required",
        raise_args=["database_url"],
        raise_kwargs={"source": "environment"},
        do_except=report_missing,
        do_else=report_present,
    )
```

For `None`, each function calls `report_missing` with the constructed exception, then raises it with
`field="database_url"` and `source="environment"`. For a defined value, `report_present` runs and the value is returned
with its narrowed type. The standalone function also accepts `exc_builder` for constructors that need a
different argument mapping; the `Buzz` method uses the class's builder automatically.
