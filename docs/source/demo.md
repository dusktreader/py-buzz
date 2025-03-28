# Demo

The `py-buzz` package includes an "extra" that can be installed to show all its features.
Each demo focuses on a particular feature and runs an examples that demonstrates how
`py-buzz` interacts with exceptions, how it affects code flow, and any side-effects it
has.


## Installation

To install the `demo` with `py-buzz` you need to supply it as an "extra" when installing `py-buzz`.
The following command can be used:

```bash
pip install py-buzz[demo]
```


## Running the demo

An entrypoint for the demo is included when it is installed. Simply run:

```bash
py-buzz-demo
```

If you provide no arguments, it will run all available demos. If you wish to only see the demos
for a particular feature, you can use the `--feature=<feature>` option to target one feature.

To see all available options, run:

```bash
py-buzz-demo --help
```

## Running the demo in an isolated environment with uv

If you want to run the demo but not include its dependencies in your system python
or an activated virtual environment, you can execute the demo with uv:

```bash
uv run --with=py-buzz[demo] py-buzz-demo
```


## Check out the source

You can also examine the demo source to examine how `py-buzz` is used.

Check out the [source code on Github](https://github.com/dusktreader/py-buzz/tree/main/src/demo).
