# Features

## Main Features

There are a few main features of `py-buzz` that are noteworthy:


### Raise exception on condition failure

The `py-buzz` package provides a function that checks a condition and raises
an exception if it fails. This is nice, because you often find your self writing
a lot of `if <whatever>: raise Exception(<message>)` throughout your code
base. It's just a little easier with `py-buzz`:

```python
# Vanilla python
if not some_condition():
    raise Exception("some_condition failed")

# With py-buzz
require_condition(some_condition(), "some_condition failed")
```

This is mostly just a bit of syntactic sugar, but it can make your code a bit more
palatable. This is especially true in functions that need to check a lot of conditions
before prior to executing their core logic.

You may also specify the exception type that should be raised by passing it to the
`raise_exc_class` parameter:

```python
require_condition(
    some_condition(),
    "some_condition failed",
    raise_exc_class=MyProjectError,
)
```

In this case, a `MyProjectError` would be raised if the condition fails.

There are a few special keyword argument parameters for the `require_condition()`
function:


#### raise_exc_class

This just specifies the type of exception to raise if the condition fails.
It defaults to `Exception`.


#### raise_args

With this parameter, you can specify any positional arguments that should be passed
to the raised exception _after the message_. Here is an example:

```python

class MyProjectError(Exception):
    def __init__(self, message, init_arg1, init_arg2):
        self.init_arg1 = init_arg1
        self.init_arg2 = init_arg2

require_condition(
    some_condition(),
    "some_condition failed",
    raise_exc_class=MyProjectError,
    raise_args=["foo", "bar"],
)
```

If the condition fails, `require_condition` will rais a `MyProjectError` initialized
with positional args `init_arg1 == "foo"` and `init_arg2 == "bar"`.


#### raise_kwargs

Like the `raise_args` parameter, this one passes along a dictionary of keyword arguments
to the newly raised exception:


```python
class MyProjectError(Exception):
    def __init__(self, message, init_kwarg1=None, init_kwarg2=None):
        self.init_kwarg1 = init_kwarg1
        self.init_kwarg2 = init_kwarg2

require_condition(
    some_condition(),
    "some_condition failed",
    raise_exc_class=MyProjectError,
    raise_kwargs=dict("foo", "bar"),
)
```

If the condition fails, `require_condition` will rais a `MyProjectError` initialized
with keyword arguments `init_kwarg1 == "foo"` and `init_kwarg2 == "bar"`.


#### exc_builder

If the exception to be raised with the `raise_exc_class` option is a non-standard
exception type that does not take a string message as its first argument, you will need
to use an alternative exception builder that knows how to map the exception parts to the
correct place.

For example, [FastAPI](https://fastapi.tiangolo.com/)'s `HTTPException` takes a
`status_code` as its first positional argument and expects that any message details are
passed as a keyword argument named `details`.

In this case, you need to define a builder function to construct the exception and pass
it to the `exc_builder` option. The `exc_builder` option should be a callable function
that accepts a single parameter of type `ExcBuilderParams` that can be imported from
``buzz``.


```python
class WeirdArgsError(Exception):
    def __init__(self, *args, detail="", **kwargs):
        self.detail = detail
        super().__init__(*args, **kwargs)

def weird_builder(params):
    return exc_class(*params.raise_args, detail=params.message, **params.raise_kwargs)

require_condition(
    some_condition(),
    "some_condition failed",
    raise_exc_class=WeirdArgsError,
    raise_args=["jawa"],
    raise_kwargs=dict("ewok"="hutt")
    exc_builder=weird_builder,
)
```


### Raise exception if value is not defined

The `py-buzz` package provides a function that checks a value and raises an exception if
it is not defined. This is especially useful for both checking if a variable passed to a
function is defined and also to satisfy static type checkers when you want to call a
method on the object.

```python
    # Vanilla python
    def vanilla(val: Optional[str]) -> str:
        if val is None:
            raise Exception("Received an undefined value!")
        return val.upper()

    # With py-buzz
    def buzzy(val: Optional[str]) -> str:
        val = enforce_defined(val)
        return val.upper()
```

This is also mostly just syntactic sugar, but it can save you a few lines of code and is
still very expressive. It might also be useful if you need to supply some more context
in your error:

```python
def neopolitan(val: Optional[str]):
    val = enforce_defined(
        val,
        "Received an undefined value!"
        raise_exc_class=MyProjectError,
        raise_args=["jawa", "ewok"],
        raise_kwargs=dict(hutt="pyke"),
    )
    return val
```

In this case, a `MyProjectError` with be raised with positional arguments of `"jawa"` and
`"ewok"` and a keyword argument of `hutt="pyke"` if the value passed in is not defined.

By default, `enforce_defined()` raises an exception with a basic message saying that the
value was not defined. However, you may pass in a custom message with the `message`
keyword argument.

The `enforce_defined()` function also accepts some keyword arguments:


#### raise_exc_class

Functions the same as `require_condition`.


#### raise_args

Functions the same as `require_condition`.


#### raise_kwargs

Functions the same as `require_condition`.


#### exc_builder

Functions the same as `require_condition`.



### Exception handling context manager

The `py-buzz` package also provides a context manager that catches any exceptions that
might be raised while executing a bit of code. The caught exceptions are re-packaged and
raised as another exception type. The message attached to the new expression captures the
initial exception's message:

```python
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

This actually can save a bit of code and makes things a bit cleaner. It is also a
implements pattern that tends to get repeated over and over again. If you need to do
very complicated things while handling an exception, you should use a standard try-
catch block. However, there are some extra bells and whistles on `handle_errors` that
can be used by passing additional keyword arguments to the function.


#### raise_exc_class

This parameter is the same as for `require_condition()`. However, if you pass `None` it
_will not raise a new exception_. Instead, `handle_errors` will process the `do_except`,
`do_else`, and `do_finally` methods and then continue. This effectively absorbs any
exceptions that occur in the context. However *the context is immediately exited after
the first raised exception*.


#### raise_args

Functions the same as `require_condition`.


#### raise_kwargs

Functions the same as `require_condition`.


#### exc_builder

Functions the same as `require_condition`.


#### handle_exc_class

This option describes the type of exception that will be handled by this context
manager. Any instance of the option's exception (or any of its derived exception
classes) will be caught. This is very useful if you only want to handle a certain
category of exceptions and let the others rise up un-altered:

```python
with handle_errors("Something went wrong", handle_exc_class=MyProjectError):
    some_function_that_could_raise_mine_or_other_errors()
```

Exception instances that do not fall within the inheritance tree of the
`handle_exc_class` option _will not be handled at all_. It is worth noting that the
`do_except` task will _not_ be executed if another exception type occurs. However,
the `do_else` and `do_finally` tasks will be executed normally.


#### ignore_exc_class

This option describes a type of exception that should _not_ be handled by this
context manager. Any instance of the option's exception (or any of its derived
exception classes) will be raised immediately by `handle_errors` and will be not
be handled or processed.

This is useful if you want a specific variant of your `handle_exc_class` to not
be handled by `handle_errors`. For example, if you want to use
`handle_exc_class=Exception` but you do not want `handle_errors` to handle
`RuntimeError`, then, you would set `ignore_exc_class=RuntimeError`.


#### do_except

Often, it is useful to do some particular things when an exception is caught.  Most
frequently this includes logging the exception. The `do_except` optional argument
provides the ability to do this. The `do_except` option should be a callable function
that accepts a parameter of type `DoExceptParams` that can be imported from ``buzz``.
This `dataclass` has three attributes:

* err: The caught exception itself
* base_message: The message provided as the first argument to `handle_errors`
* final_message: A message describing the error (This will be the formatted error message)
* trace: A stack trace

This option might be invoked something like this:

```python
def log_error(dep: DoExceptParams):
    logger.error(dep.final_message)
    logger.error('\n'.join(dep.trace))

with handle_errors("Something went wrong", do_except=log_error):
    some_dangerous_function()
```


#### do_else

This option describes some action that should happen if no exceptions are encountered.
This option is less useful than `do_except` but it may useful in some circumstances.
This option should be a callable that takes no arguments:

```python
    def log_yay():
        logger.info("we did it!")

    with handle_errors("Something went wrong", do_else=log_yay):
        some_not_dangerous_function()
```


#### do_finally

This option describes some action that should happen at the end of the context
regardless to whether an exception occurred or not. This is a useful feature if you need
to do some cleanup in either case. It should take a callable that receives no arguments:

```python
def close_resource():
    resource.close()

with handle_errors("Something went wrong", do_finally=close_resource):
    some_dangerous_function_that_uses_resource(resource)
```

#### exc_builder

Functions the same as `require_condition`.


### check_expressions

The `check_expressions` context manager is used to check multiple expressions inside of
a context manager. Each expression is checked and each failing expression is reported at
the end in a raised exception. If no expressions fail in the block, no exception is
raised.

```python
with check_expressions(main_message='there will be errors') as check:
    check(True)
    check(False)
    check(1 == 2, "one is not two")
    check('cooooooool', 'not a problem')
    check(0, "zero is still zero")
```

If the above code was executed, an exception would be raised that looks like this:

```
Exception: Checked expressions failed: there will be errors
   2: 2nd expression failed
   3: one is not two
   5: zero is still zero
```

The `check_expressions()` context manager also accepts some keyword arguments:


#### raise_exc_class

Functions the same as `require_condition`.


#### raise_args

Functions the same as `require_condition`.


#### raise_kwargs

Functions the same as `require_condition`.


#### exc_builder

Functions the same as `require_condition`.


## Additional Features

### reformat_exception

This method is used internally by the `handle_errors` context manager.  However, it is
sometimes useful in other circumstances. It simply allows you to wrap an exception
message in a more informative block of text:

```python
try:
    raise ValueError("I didn't like that")
except Exception as err:
    print(reformat_exception("welp...that didn't work", err))
```

The above block would result in output like:

```
> welp...that didn't work -- ValueError: I didn't like that
```


### get_traceback

This function is just a tool to fetch the traceback for the current function. It does
this by fetching it out of `sys.exc_info`. It is used internally with Buzz but could
be useful in other contexts.


## The Buzz base class

All of the methods described above are attached to the special exception class, `Buzz`.
You could, for example, use this as the base exception type for your project and then
access all the functions of `py-buzz` from that exception type:

```python
from buzz import Buzz

class MyProjectError(Buzz):
    pass

MyProjectError.require_condition(check_vals(), "Value check failed!")
```

The code above would raise a `MyProjectError` with the supplied message if the condition
expression was falsey.

The `Buzz` base class provides the same sort of access for `handle_errors`,
`enforce_defined`, and `check_expressions`.


## Demo

The `py-buzz-demo` executable (only available when installed with the `demo` extra) shows
the features described here in action. See the [Demo](./demo.md) page for more info.
