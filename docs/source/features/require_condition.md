# Require a condition

`require_condition()` checks a condition and raises an exception when it fails. It saves you from scattering the same
`if <whatever>: raise Exception(<message>)` pattern throughout your code, with a little less repetition.


## Basic use

```python {linenums="1"}
from buzz import require_condition

# Vanilla python
if not some_condition():
    raise Exception("some_condition failed")

# With py-buzz
require_condition(some_condition(), "some_condition failed")
```

It is a small bit of syntactic sugar, but it can make functions with lots of checks easier to read.

For a `Buzz` subclass, the class method binds the exception type:

```python {linenums="1"}
from buzz import Buzz, require_condition

class ConfigError(Buzz):
    pass

require_condition(config_is_valid(), "Invalid configuration", raise_exc_class=ConfigError)
ConfigError.require_condition(config_is_valid(), "Invalid configuration")
```


## Advanced use

Use callbacks to observe both outcomes, and constructor arguments to attach structured context to the failure. The
standalone function takes an explicit exception class; a `Buzz` subclass method binds its own type and builder:

```python {linenums="1"}
from buzz import Buzz, require_condition


class ConfigException(Exception):
    def __init__(self, message: str, setting: str, *, source: str):
        self.setting = setting
        self.source = source
        super().__init__(message)


def report_failure(exc: Exception) -> None:
    print(f"Configuration check failed: {exc}")


def report_success() -> None:
    print("Configuration is valid")


def check_config(enabled: bool) -> None:
    require_condition(
        enabled,
        "Configuration is disabled",
        raise_exc_class=ConfigException,
        raise_args=["feature flag"],
        raise_kwargs={"source": "startup"},
        do_except=report_failure,
        do_else=report_success,
    )


class ConfigError(Buzz):
    def __init__(self, message: str, setting: str, *, source: str, base_message: str | None = None):
        self.setting = setting
        self.source = source
        super().__init__(message, base_message=base_message)


def check_config_with_buzz(enabled: bool) -> None:
    ConfigError.require_condition(
        enabled,
        "Configuration is disabled",
        raise_args=["feature flag"],
        raise_kwargs={"source": "startup"},
        do_except=report_failure,
        do_else=report_success,
    )
```

When `enabled` is false, each function constructs its configured exception with `setting="feature flag"` and
`source="startup"`, calls `report_failure` with that exception, and then raises
it. When it is true, `report_success` runs and the check returns normally.


### `exc_builder`

A custom builder can adapt an exception whose constructor does not accept the message first. It receives
`ExcBuilderParams`, including the selected exception class, message, positional arguments, and keyword arguments:

```python {linenums="1"}
from buzz import require_condition
from buzz.tools import ExcBuilderParams


class StatusError(Exception):
    def __init__(self, status_code: int, *, detail: str, source: str):
        self.status_code = status_code
        self.detail = detail
        self.source = source
        super().__init__(detail)


def build_status_error(params: ExcBuilderParams) -> Exception:
    return params.raise_exc_class(
        *params.raise_args,
        detail=params.message,
        **params.raise_kwargs,
    )


require_condition(
    False,
    "The account is inactive",
    raise_exc_class=StatusError,
    raise_args=[403],
    raise_kwargs={"source": "account check"},
    exc_builder=build_status_error,
)
```

The builder maps the check's message to `detail`, while `raise_args` supplies `status_code` and `raise_kwargs` supplies
`source`. This example uses a local non-Buzz exception rather than assuming a particular web framework's constructor.

A `Buzz` subclass binds its own builder for the equivalent class-method call.
Override `exc_builder` on the class to adapt its nonstandard constructor:

```python {linenums="1"}
from typing_extensions import Self

from buzz import Buzz, require_condition
from buzz.tools import ExcBuilderParams


class AccountError(Buzz):
    def __init__(self, status_code: int, *, detail: str, source: str, base_message: str | None = None):
        self.status_code = status_code
        self.detail = detail
        self.source = source
        super().__init__(detail, base_message=base_message)

    @classmethod
    def exc_builder(cls, params: ExcBuilderParams) -> Self:
        return cls(
            *params.raise_args,
            detail=params.message,
            base_message=params.base_message,
            **params.raise_kwargs,
        )


AccountError.require_condition(
    False,
    "The account is inactive",
    raise_args=[403],
    raise_kwargs={"source": "account check"},
)
```
