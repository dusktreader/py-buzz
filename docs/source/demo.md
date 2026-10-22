# Demo

The optional `demo` extra comes with executable examples of the `py-buzz` helpers.
Each one shows how a helper shapes exception handling and program flow.


## Installation

The demo is an optional extra, so it joins `py-buzz` when the package is installed with:

```shell
uv pip install 'py-buzz[demo]'
```


## Running the demo

Installing the extra also adds a demo entrypoint:

```shell
py-buzz-demo
```

With no arguments, the entrypoint runs all available demos. To focus on one feature, the `--feature=<feature>` option
selects its demos.

The full list of options is available with:

```shell
py-buzz-demo --help
```


## Running the demo in an isolated environment with uv

The demo can run through `uv` without adding its dependencies to your system Python or an activated virtual environment:

```shell
uvx --from='py-buzz[demo]' py-buzz-demo
```


## Demo source

The demo source offers a closer look at how `py-buzz` fits into the examples.

The [source code on Github](https://github.com/dusktreader/py-buzz/tree/main/src/buzz_demo) is available for browsing.
