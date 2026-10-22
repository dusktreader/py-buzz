# Handle errors in a context manager

The `handle_errors()` context manager catches exceptions raised inside a block and re-raises them as
another exception type. The new exception's message includes the original message.


## Synchronous use

```python {linenums="1"}
from buzz import handle_errors

# Vanilla python
try:
    this_could_fail()
    this_could_also_fail()
    this_will_definitely_fail()
except Exception as err:
    raise RuntimeError(f"Something didn't work -- Error: {err}")

# With py-buzz
with handle_errors("Something didn't work", raise_exc_class=RuntimeError):
    this_could_fail()
    this_could_also_fail()
    this_will_definitely_fail()
```

This context manager trims some repeated exception-handling code. For more involved handling, a standard `try`/`except`
block may be a better fit. A `Buzz` subclass method binds the exception type for you:

```python {linenums="1"}
from buzz import Buzz, handle_errors

class ConfigError(Buzz):
    pass

with handle_errors("Could not load configuration", raise_exc_class=ConfigError):
    load_config()

with ConfigError.handle_errors("Could not load configuration"):
    load_config()
```


## Advanced use

Filters decide which failures are wrapped. In synchronous use, callbacks receive the original
failure context, and constructor arguments are passed to the replacement exception:

```python {linenums="1"}
from buzz import Buzz, DoExceptParams, handle_errors


class DataException(Exception):
    def __init__(self, message: str, dataset: str, *, source: str):
        self.dataset = dataset
        self.source = source
        super().__init__(message)


def report_error(params: DoExceptParams) -> None:
    print(f"{params.base_message}: {params.err}")
    print(params.final_message)


def report_success() -> None:
    print("Data loaded")


def close_data_source() -> None:
    print("Data source closed")


def load_data() -> None:
    with handle_errors(
        "Could not load customer data",
        raise_exc_class=DataException,
        raise_args=["customers"],
        raise_kwargs={"source": "warehouse"},
        handle_exc_class=Exception,
        ignore_exc_class=RuntimeError,
        do_except=report_error,
        do_else=report_success,
        do_finally=close_data_source,
    ):
        read_customer_rows()


class DataError(Buzz):
    def __init__(self, message: str, dataset: str, *, source: str, base_message: str | None = None):
        self.dataset = dataset
        self.source = source
        super().__init__(message, base_message=base_message)


def load_data_with_buzz() -> None:
    with DataError.handle_errors(
        "Could not load customer data",
        raise_args=["customers"],
        raise_kwargs={"source": "warehouse"},
        handle_exc_class=Exception,
        ignore_exc_class=RuntimeError,
        do_except=report_error,
        do_else=report_success,
        do_finally=close_data_source,
    ):
        read_customer_rows()
```

Both contexts wrap exceptions that are instances of `Exception` and not `RuntimeError` (or its subclasses) as their
configured exception. `report_error` receives a `DoExceptParams` object containing `err`, `base_message`,
`final_message`, and `trace`. `do_else` runs only when the block succeeds. Only the standalone function accepts
`raise_exc_class`; the `Buzz` method binds the class and uses `re_raise=False` to absorb handled errors.


### Async use

The async form also accepts synchronous callbacks, and can await async callbacks. Here
`do_except` is an actual async callback; it receives the same `DoExceptParams` object:

```python {linenums="1"}
from buzz import Buzz, DoExceptParams, handle_errors_async


async def record_failure(params: DoExceptParams) -> None:
    await write_audit_event(params.final_message)


async def fetch_data() -> bytes:
    async with handle_errors_async(
        "Could not fetch report",
        raise_exc_class=RuntimeError,
        handle_exc_class=(ConnectionError, TimeoutError),
        do_except=record_failure,
    ):
        return await fetch_report()


class FetchError(Buzz):
    pass


async def fetch_data_with_buzz() -> bytes:
    async with FetchError.handle_errors_async(
        "Could not fetch report",
        handle_exc_class=(ConnectionError, TimeoutError),
        do_except=record_failure,
    ):
        return await fetch_report()
```

The standalone synchronous `handle_errors()` accepts `raise_exc_class`; setting it to `None` absorbs a caught exception
after the callbacks run. The `Buzz` methods do not accept `raise_exc_class`; use `re_raise=False` to absorb handled
exceptions. By default, the context handles `Exception` and its subclasses,
not `BaseException` subclasses such as `KeyboardInterrupt` or `SystemExit`.
