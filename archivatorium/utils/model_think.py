"""Shared model-reasoning types and Click conversion."""

from typing import Literal, cast

import click

type ModelThink = Literal[False, "low", "medium", "high"]
MODEL_THINK_DEFAULT: ModelThink = "medium"
MODEL_THINK_CHOICE = click.Choice(
    ["False", "low", "medium", "high"],
    case_sensitive=False,
)


def convert_model_think(
    _ctx: click.Context,
    _param: click.Parameter,
    value: str,
) -> ModelThink:
    """Convert a validated CLI spelling to the Ollama request value."""

    normalized = value.lower()
    if normalized == "false":
        return False
    return cast(ModelThink, normalized)
