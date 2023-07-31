# py-buzz

_That's not flying, it's falling with style_

Take Exceptions to infinity...and beyond with ``py-buzz``!


## Overview

py-buzz supplies some useful tools to use with python exceptions as well
as a base Buzz exception class that includes them as classmethods.

py-buzz is fully equipped with an arsenal of helpful tools to replace boilerplate
code that appear over and over again in python projects such as:

* checking conditions and raising errors on failure (`require_conditon`)
* checking that values are defined and raising errors if not (`enforce_defined`)
* catching exceptions and wrapping them in clearer exception types with better error
  messages (`handle_errors`)
* checking many conditions and reporting which ones failed (`check_expressions`)

py-buzz provides two different main use-cases:

It provides a set of functions that can be used with any exceptions. So, if you already
have a set of custom exceptions or simply wish to use existing exceptinos, you can
use the py-buzz functions like `require_condition`, `handle_errors`, `enforce_defined`,
and so on with those pre-existing exception types.

It also prived the `Buzz` exception class that can be used  as a bass class for custom
exceptions within a project.

Either use-case allows the user to focus on clear and concise error handling in their
code base without having to re-write the same error handling code over and over or
having to re-write convenience functions themselves.


## Quickstart

### Requirements

* Python 3.8 or greater


### Installation

This will install the latest release of py-buzz from pypi via pip:

```bash
pip install py-buzz
```


### Using

Just import!

```python
from buzz import require_condition

require_condition(check_something(), "The check failed!")
```

For more examples of usage, see the [Features](features.md) page.
