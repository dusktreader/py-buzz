# Other functions

This guide covers exception utilities and retry decorators, including their standalone and `Buzz` subclass forms.


## Get a traceback

`get_traceback()` fetches the current traceback from `sys.exc_info`.
Buzz uses it internally, but it can be useful in other contexts too.


### Basic use

The standalone function and a `Buzz` subclass method both return the active
exception's traceback. Call either one inside an `except` block:

```python {linenums="1"}
from buzz import Buzz, get_traceback

class ConfigError(Buzz):
    pass

try:
    load_config()
except OSError:
    trace = get_traceback()

try:
    load_config()
except OSError:
    trace = ConfigError.get_traceback()
```


## Reformat an exception

The `handle_errors()` context manager uses `reformat_exception()` internally, though it can be handy elsewhere too. It
wraps an exception message in a more informative block of text. This
remains a standalone utility; it has no `Buzz` class method.


### Basic use

```python {linenums="1"}
from buzz import Buzz, reformat_exception

class ConfigError(Buzz):
    pass

err = ConfigError("Configuration is invalid")
print(reformat_exception("Could not load configuration", err))
```

The output looks like this:

```shell
Could not load configuration -- ConfigError: Configuration is invalid
```


## Retry decorators

`ConfigError.retry()` and `ConfigError.retry_async()` retry synchronous and asynchronous functions when they raise
selected exceptions. Retries can smooth over transient failures in network calls, APIs, and other unreliable operations.


### Standalone decorators

A custom `Buzz` subclass isn't required. The standalone decorators live in `buzz.tools` and use
`Exception` by default; `raise_exc_class` can point them at another exception type:

```python {linenums="1"}
from buzz.tools import retry, retry_async


@retry("Request failed after {attempts} attempts", retry_on=TimeoutError, raise_exc_class=RuntimeError)
def fetch_data():
    return make_request()


@retry_async("Request failed after {attempts} attempts", retry_on=TimeoutError, raise_exc_class=RuntimeError)
async def fetch_data_async():
    return await make_request_async()
```

The remaining retry options work the same as they do with a subclass's `.retry()` and `.retry_async()` methods.


### Basic use

```python {linenums="1"}
from buzz import Buzz

class ConfigError(Buzz):
    pass


# Vanilla Python
def fetch_data(url):
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except (ConnectionError, TimeoutError) as e:
            if attempt == max_attempts - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff

# With py-buzz
@ConfigError.retry("Failed to fetch data after {attempts} attempts", max_attempts=3, backoff=2.0, retry_on=(ConnectionError, TimeoutError))
def fetch_data(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
```


### Advanced use

The retry decorators control which failures trigger another attempt, how long to wait, and what to raise after the final
failure. `max_attempts` includes the initial call; `backoff` grows the delay exponentially, `max_delay` caps it, and
`jitter` randomizes each delay between zero and the calculated cap. Disable jitter here to make the timing predictable.

```python {linenums="1"}
from buzz.tools import ExcBuilderParams, retry


def build_retry_error(params: ExcBuilderParams) -> RuntimeError:
    return params.raise_exc_class(f"Retry limit reached: {params.message}")


def log_retry(attempt: int, exc: BaseException) -> None:
    print(f"Retry {attempt} after {type(exc).__name__}: {exc}")


@retry(
    "Report request failed after {attempts} attempts",
    max_attempts=4,
    backoff=2.0,
    max_delay=3.0,
    jitter=False,
    retry_on=(ConnectionError, TimeoutError),
    raise_exc_class=RuntimeError,
    exc_builder=build_retry_error,
    on_retry=log_retry,
)
def fetch_report() -> bytes:
    return request_report()
```

This standalone `buzz.tools.retry` form waits 1, 2, then 3 seconds between failed attempts, retries only connection and
timeout errors, and logs before each retry. After four failed attempts, it raises a `RuntimeError`; the final exception
is chained from the last triggering exception, so its `__cause__` retains the last failure.

A `Buzz` subclass method binds the final exception type and builder. It
still accepts the retry controls, callback, and constructor arguments:

```python {linenums="1"}
from buzz import Buzz


class ServiceError(Buzz):
    def __init__(self, message: str, service: str, *, request_id: str, base_message: str | None = None):
        self.service = service
        self.request_id = request_id
        super().__init__(message, base_message=base_message)


@ServiceError.retry(
    "Inventory lookup failed after {attempts} attempts",
    max_attempts=3,
    backoff=1.5,
    max_delay=2.0,
    jitter=True,
    retry_on=TimeoutError,
    raise_args=["inventory"],
    raise_kwargs={"request_id": "req-42"},
    on_retry=log_retry,
)
def lookup_inventory() -> dict[str, int]:
    return request_inventory()
```

The default `retry_on=Exception` catches `Exception` and its subclasses, not subclasses of `BaseException` such as
`KeyboardInterrupt` or `SystemExit`. Exceptions outside the selected `retry_on` types pass through immediately.


### Asynchronous retries

`retry_async` and `.retry_async()` use `asyncio.sleep()` between attempts. Their
`on_retry` callback remains synchronous, even when decorating an async function:

```python {linenums="1"}
from buzz.tools import retry_async


@retry_async(
    "Async request failed after {attempts} attempts",
    max_attempts=3,
    backoff=2.0,
    max_delay=2.5,
    jitter=False,
    retry_on=(ConnectionError, TimeoutError),
    raise_exc_class=RuntimeError,
    exc_builder=build_retry_error,
    on_retry=log_retry,
)
async def fetch_report_async() -> bytes:
    return await request_report_async()


class AsyncServiceError(Buzz):
    def __init__(self, message: str, service: str, *, request_id: str, base_message: str | None = None):
        self.service = service
        self.request_id = request_id
        super().__init__(message, base_message=base_message)


@AsyncServiceError.retry_async(
    "Async inventory lookup failed after {attempts} attempts",
    max_attempts=3,
    backoff=2.0,
    max_delay=2.5,
    jitter=False,
    retry_on=TimeoutError,
    raise_args=["inventory"],
    raise_kwargs={"request_id": "req-43"},
    on_retry=log_retry,
)
async def lookup_inventory_async() -> dict[str, int]:
    return await request_inventory_async()
```

Both standalone decorators are imported from `buzz.tools`. They accept `raise_exc_class` and `exc_builder`; the `Buzz`
methods bind those automatically. All forms accept `raise_args`, `raise_kwargs`, and a synchronous `on_retry` callback.
