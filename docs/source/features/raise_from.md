# Raise an exception from another

When exception handling is already in your hands, `raise_from()` is an alternative to the `handle_errors()` context
manager. The new exception keeps the original as its cause, so Python's traceback shows both errors.


## Basic use

```python {linenums="1"}
from buzz import raise_from

try:
    load_profile()
except OSError as err:
    raise_from("Could not load profile", err, raise_exc_class=RuntimeError)
```

The default message includes the base message, the original exception type, and its message.


## With a `Buzz` subclass

For a `Buzz` subclass, its class method raises an instance of that exception type, without passing `raise_exc_class`:

```python {linenums="1"}
from buzz import Buzz


class ProfileError(Buzz):
    pass


try:
    load_profile()
except OSError as err:
    ProfileError.raise_from("Could not load profile", err)
```


## Advanced use

Both forms accept a final message, an explicit traceback, and extra constructor arguments. The standalone function also
accepts a custom exception builder. In either case, the original exception remains the new exception's `__cause__`:

```python {linenums="1"}
from buzz import Buzz, raise_from
from buzz.tools import ExcBuilderParams


# Standalone custom builder
def build_profile_error(params: ExcBuilderParams) -> RuntimeError:
    return params.raise_exc_class(
        f"{params.message} (store={params.raise_args[0]}, region={params.raise_kwargs['region']})"
    )


def load_with_standalone() -> None:
    try:
        load_profile()
    except OSError as err:
        original = err
        try:
            raise_from(
                "Could not load profile",
                err,
                raise_exc_class=RuntimeError,
                raise_args=["profile-store"],
                raise_kwargs={"region": "west"},
                exc_builder=build_profile_error,
                final_message="Profile storage is unavailable",
                trace=err.__traceback__,
            )
        except RuntimeError as wrapped:
            assert wrapped.__cause__ is original
            raise


# Buzz subclass with its own constructor
class ProfileError(Buzz):
    def __init__(self, message: str, store: str, *, region: str, base_message: str | None = None):
        self.store = store
        self.region = region
        super().__init__(message, base_message=base_message)


def load_with_buzz_class() -> None:
    try:
        load_profile()
    except OSError as err:
        original = err
        try:
            ProfileError.raise_from(
                "Could not load profile",
                err,
                raise_args=["profile-store"],
                raise_kwargs={"region": "west"},
                final_message="Profile storage is unavailable",
                trace=err.__traceback__,
            )
        except ProfileError as wrapped:
            assert wrapped.__cause__ is original
            raise
```

`trace=err.__traceback__` explicitly attaches the original traceback; when omitted, the helper uses the active
exception's traceback. `final_message` replaces the formatted default when it is a non-empty string.
`raise_args` and `raise_kwargs` are passed to the exception constructor after the message.
