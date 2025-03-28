from __future__ import annotations

# When Python 3.9 is no longer supported, remove Optional
from typing import Annotated, Optional
from collections.abc import Callable

import snick
import typer
from auto_name_enum import AutoNameEnum, auto
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Confirm

from demo.helpers import run_demo, get_demo_functions


class Feature(AutoNameEnum):
    check_expressions = auto()
    handle_errors = auto()
    enforce_defined = auto()
    require_condition = auto()
    with_buzz_class = auto()
    using_exc_builder = auto()


def start(
    feature: Annotated[Optional[Feature], typer.Option(
        help="The feature to demo. If not provided, demo ALL",
    )] = None,
):
    """
    This cli app will demo the features of `py-buzz`!

    Note: If no features are selected for the demo, all of them will be shown.
    """
    features: list[Feature]
    if feature is None:
        features = [f for f in Feature]
    else:
        features = [feature]

    feature_map: dict[Feature, list[Callable[..., None]]] = {}
    for feature in features:
        feature_map[feature] = get_demo_functions(feature)

    override_label_map: dict[Feature, str] = {
        Feature.with_buzz_class: "Buzz",
        Feature.using_exc_builder: "exc_builder",
    }

    greeting_lines = [
        "Welcome to the `py-buzz` demo!",
        "",
        "This program will show you the different features available in `py-buzz` and what it's like to use them",
        "",
        "The following features will be included:",
    ]
    for feature in features:
        label = override_label_map.get(feature, f"{feature}()")
        greeting_lines.append(f"- `{label}`")
        for demo in feature_map[feature]:
            greeting_lines.append(f"  - `{demo.__name__}()`")

    console = Console()
    console.clear()
    console.print(
        Panel(
            Markdown(snick.conjoin(*greeting_lines)),
            padding=1,
            title="[green]Welcome to py-buzz![/green]",
            subtitle="[blue]https://github.com/dusktreader/py-buzz[/blue]",
        )
    )
    console.print()
    console.print()
    further: bool = Confirm.ask("Would you like to continue?", default=True)
    if not further:
        return

    for feature, demos in feature_map.items():
        for demo in demos:
            further = run_demo(demo, console, override_label=override_label_map.get(feature))
            if not further:
                break

    console.clear()
    console.print(
        Panel(
            Markdown(
                snick.dedent(
                    """
                    Thanks for checking out `py-buzz`!

                    I hope these features will be useful for you.

                    If you would like to learn more, please check out the
                    [documentation site](https://dusktreader.github.io/py-buzz/)
                    """
                ),
            ),
            padding=1,
            title="[green]Thanks![/green]",
            subtitle="[blue]https://github.com/dusktreader/py-buzz[/blue]",
        )
    )
    console.print()
    console.print()


def main():
    typer.run(start)
