"""
This module provides helpers for the main demo executable.
"""
from __future__ import annotations

import io
import inspect
import re
import sys
import textwrap
from importlib import import_module
from typing import Any
from collections.abc import Callable
from dataclasses import dataclass

import snick
from rich import box
from rich.console import Console, Group, RenderableType
from rich.panel import Panel
from rich.prompt import Confirm
from rich.markdown import Markdown
from rich.rule import Rule


@dataclass
class Decomposed:
    module: str
    name: str
    docstring: str
    source: str


@dataclass
class Captured:
    error: Exception | None = None
    output: str | None = None

BlankLine = Rule(characters=" ")


def get_demo_functions(module_name: str) -> list[Callable[..., None]]:
    demo_functions: list[Callable[..., None]] = []
    module = import_module(f"demo.{module_name}")
    for _, obj in inspect.getmembers(module):
        if inspect.isfunction(obj) and obj.__name__.startswith("demo"):
            demo_functions.append(obj)
    return sorted(demo_functions, key=lambda f: f.__name__)



def decompose(func: Callable[..., Any]) -> Decomposed:
    """
    This is really hacky.

    Maybe improve this sometime.
    """
    module = func.__module__.split(".")[-1]
    name = func.__name__

    if func.__doc__ is None:
        raise RuntimeError("Can't demo a function with no docstring!")
    docstring = textwrap.dedent(func.__doc__).strip()

    source_lines = inspect.getsourcelines(func)[0]
    first_quotes = False
    code_start_index = 0
    for i, line in enumerate(source_lines):
        if line.strip() == '"""':
            if not first_quotes:
                first_quotes = True
            else:
                code_start_index = i
                break
    if code_start_index == 0:
        raise RuntimeError("Failed to strip function declaration and docstring!")
    source_lines = [re.sub(r'\s+# pyright.*', '', sl) for sl in source_lines]
    source_lines = [re.sub(r'\s+# type.*', '', sl) for sl in source_lines]
    source = textwrap.dedent("".join(source_lines[code_start_index+1:]))

    return Decomposed(module=module, name=name, docstring=docstring, source=source)


def capture(demo: Callable[..., None]) -> Captured:
    cap = Captured()

    string_buffer = io.StringIO()
    original_stdout = sys.stdout
    sys.stdout = string_buffer

    try:
        demo()
    except Exception as exc:
        cap.error = exc
    finally:
        sys.stdout = original_stdout

    dump = string_buffer.getvalue()
    if dump:
        cap.output = dump

    return cap


def run_demo(demo: Callable[..., None], console: Console, override_label: str | None = None) -> bool:
    console.clear()

    decomposed = decompose(demo)
    cap: Captured = capture(demo)

    parts: list[RenderableType] = [
        Markdown(decomposed.docstring),
        BlankLine,
        BlankLine,
        Panel(
            Markdown(
                "\n".join([
                    "```python",
                    decomposed.source,
                    "```",
                ])
            ),
            title=f"Here is the source code for [yellow]{decomposed.name}()[/yellow]",
            title_align="left",
            padding=1,
            expand=False,
            box=box.SIMPLE,
        ),
    ]

    if cap.output:
        parts.extend([
            BlankLine,
            BlankLine,
            Panel(
                Markdown(
                    snick.conjoin(
                        "```text",
                        cap.output,
                        "```"
                    ),
                ),
                title=f"Here is the output captured from [yellow]{decomposed.name}()[/yellow]",
                title_align="left",
                padding=1,
                expand=False,
                box=box.SIMPLE,
            ),
        ])

    if cap.error:
        parts.extend([
            BlankLine,
            BlankLine,
            Panel(
                f"[red]{cap.error.__class__.__name__}[/red]: [yellow]{str(cap.error)}[/yellow]",
                title=f"Here is the uncaught exception from [yellow]{decomposed.name}()[/yellow]",
                title_align="left",
                padding=1,
                expand=False,
                box=box.SIMPLE,
            )
        ])

    label = override_label if override_label else f"{decomposed.module}()"
    console.print(
        Panel(
            Group(*parts),
            padding=1,
            title=f"Showing [yellow]{decomposed.name}()[/yellow] for [green]{label}[/green]",
            title_align="left",
            subtitle="[blue]https://github.com/dusktreader/py-buzz[/blue]",
            subtitle_align="left",
        ),
    )
    console.print(BlankLine)
    console.print(BlankLine)
    further: bool = Confirm.ask("Would you like to continue?", default=True)
    return further
