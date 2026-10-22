# Ensure a value has the right type

`ensure_type()` checks that a value has the expected runtime type and raises an exception if it does not. On success, it
returns the value with a narrowed type, which helps static type checkers follow along.


## Basic use

```python {linenums="1"}
from buzz import ensure_type

# Vanilla python
def vanilla(val: str | int) -> str:
    if not isinstance(val, str):
        raise Exception("Received a non-string value!")
    return val.upper()

# With py-buzz
def buzzy(val: str | int) -> str:
    return ensure_type(val, str).upper()
```

`ensure_type()` checks the runtime type; it does not cast the value. A basic message explains when the value has
the wrong type, and the `message` keyword argument lets you provide a custom one.

A `Buzz` subclass method binds the exception type, so its call is shorter:

```python {linenums="1"}
from buzz import Buzz, ensure_type

class ConfigError(Buzz):
    pass

name = ensure_type(config_value, str, "Expected a string", raise_exc_class=ConfigError)
name = ConfigError.ensure_type(config_value, str, "Expected a string")
```


## Advanced use

Use a custom non-Buzz exception to record which field failed validation, and callbacks to distinguish rejection from
success. Both forms below pass an explicit message; the `Buzz.ensure_type()` default currently
contains the literal `{type_}` rather than formatting the expected type into it.

```python {linenums="1"}
from buzz import Buzz, ensure_type


class TypeValidationError(Exception):
    def __init__(self, message: str, field: str, *, source: str):
        self.field = field
        self.source = source
        super().__init__(message)


def report_type_error(exc: Exception) -> None:
    print(f"Invalid configuration: {exc}")


def report_valid_value() -> None:
    print("Configuration value has the expected type")


def read_database_url(value: object) -> str:
    return ensure_type(
        value,
        str,
        "database_url must be a string",
        raise_exc_class=TypeValidationError,
        raise_args=["database_url"],
        raise_kwargs={"source": "environment"},
        do_except=report_type_error,
        do_else=report_valid_value,
    )


class TypeValidationBuzzError(Buzz):
    def __init__(self, message: str, field: str, *, source: str, base_message: str | None = None):
        self.field = field
        self.source = source
        super().__init__(message, base_message=base_message)


def read_database_url_with_buzz(value: object) -> str:
    return TypeValidationBuzzError.ensure_type(
        value,
        str,
        "database_url must be a string",
        raise_args=["database_url"],
        raise_kwargs={"source": "environment"},
        do_except=report_type_error,
        do_else=report_valid_value,
    )
```

On mismatch, each form constructs its configured exception with the field and source, passes that exception to
`report_type_error`, then raises it. On a match, `report_valid_value` runs and the value is returned with its narrowed
type. The standalone function also accepts `exc_builder`; the `Buzz` method binds the exception class and builder.
