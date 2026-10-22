# Verify a literal value

`verify_literal()` checks a value against a `typing.Literal` type and raises an exception if the value is not allowed.
Like `ensure_type()`, it returns the value on success, so it fits naturally into an expression.

The `verify_literal()` function uses `TypeForm` to narrow the type of the return value, so
type checkers will accept the verified string as an instance of the string literal.


## Basic use

```python {linenums="1"}
from typing import Literal, cast

from buzz import verify_literal

Species = Literal["jawa", "ewok", "pyke"]

# Vanilla python
def vanilla(val: str) -> Species:
    if val not in ("jawa", "ewok", "pyke"):
        raise Exception("Received an unexpected value!")
    return cast(Species, val)

# With py-buzz
def buzzy(val: str) -> Species:
    return verify_literal(val, Literal["jawa", "ewok", "pyke"])
```

A `Buzz` subclass method also binds the exception type:

```python {linenums="1"}
from typing import Literal

from buzz import Buzz, verify_literal

Species = Literal["jawa", "ewok", "pyke"]


class ConfigError(Buzz):
    pass


def buzzy(val: str) -> Species:
    return ConfigError.verify_literal(val, Species)
```


## Advanced use

Both forms return the accepted value, run `do_else` on success, and pass the exception being raised to
`do_except` on an invalid value. Constructor arguments can attach context to the error:

```python {linenums="1"}
from typing import Literal

from buzz import Buzz, verify_literal

Species = Literal["jawa", "ewok", "pyke"]


class SpeciesError(Exception):
    def __init__(self, message: str, species_code: int, *, field: str):
        self.species_code = species_code
        self.field = field
        super().__init__(message)


def record_rejection(exc: Exception) -> None:
    print(f"Rejected unknown species: {exc}")


def record_accepted() -> None:
    print("Well known species accepted")


def parse_species(species: str) -> Species:
    return verify_literal(
        species,
        Species,
        "Unknown species",
        raise_exc_class=SpeciesError,
        raise_args=[400],
        raise_kwargs={"field": "species"},
        do_except=record_rejection,
        do_else=record_accepted,
    )


class SpeciesBuzzError(Buzz):
    def __init__(
        self,
        message: str,
        species_code: int,
        *,
        field: str,
        base_message: str | None = None,
    ):
        self.species_code = species_code
        self.field = field
        super().__init__(message, base_message=base_message)


def parse_species_with_buzz(species: str) -> Species:
    return SpeciesBuzzError.verify_literal(
        species,
        Species,
        "Unknown species",
        raise_args=[400],
        raise_kwargs={"field": "species"},
        do_except=record_rejection,
        do_else=record_accepted,
    )
```

For an unknown value, each form constructs its configured exception with `species_code=400` and `field="species"`, calls
the rejection callback, and raises. For an allowed value, they call `record_accepted` and return it. A non-`Literal`
type raises `TypeError` immediately. Python permits enum members in runtime `Literal` values, but `verify_literal()`'s
current `LiteralElement` annotation excludes enums, so static type checkers may reject those annotations.
