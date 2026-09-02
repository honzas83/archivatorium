from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from archivatorium.cli import cli


def _metadata_args(tmp_path: Path, value: str | None = None) -> list[str]:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir(exist_ok=True)
    hierarchy = tmp_path / "themes.yaml"
    tags = tmp_path / "tags.yaml"
    hierarchy.write_text("categories: []\n", encoding="utf-8")
    tags.write_text("useful_tags: []\n", encoding="utf-8")
    args = [
        "metadata",
        str(input_dir),
        str(output_dir),
        "--hierarchy-file",
        str(hierarchy),
        "--tags-file",
        str(tags),
    ]
    return args + (["--model-think", value] if value is not None else [])


def _ocr_args(tmp_path: Path, value: str | None = None) -> list[str]:
    input_dir = tmp_path / "ocr-input"
    output_dir = tmp_path / "ocr-output"
    input_dir.mkdir(exist_ok=True)
    args = ["ocr", str(input_dir), str(output_dir)]
    return args + (["--model-think", value] if value is not None else [])


@pytest.mark.parametrize(
    ("cli_value", "request_value"),
    [("False", False), ("FALSE", False), ("LoW", "low"), ("MEDIUM", "medium"), ("High", "high")],
)
@pytest.mark.parametrize("command", ["metadata", "ocr"])
def test_model_think_is_case_insensitive_and_typed(
    tmp_path: Path, command: str, cli_value: str, request_value: bool | str
) -> None:
    runner = CliRunner()
    with (
        patch("archivatorium.cli.MetadataProcessor") as metadata_processor,
        patch("archivatorium.cli.TaggingService"),
        patch("archivatorium.cli.OllamaClient"),
        patch("archivatorium.ocr_engine.OCREngine") as ocr_engine,
    ):
        metadata_processor.return_value.get_files.return_value = []
        args = (
            _metadata_args(tmp_path, cli_value)
            if command == "metadata"
            else _ocr_args(tmp_path, cli_value)
        )
        result = runner.invoke(cli, args)

    assert result.exit_code == 0, result.output
    boundary = metadata_processor if command == "metadata" else ocr_engine
    assert boundary.call_args.kwargs["model_think"] == request_value


@pytest.mark.parametrize("command", ["metadata", "ocr"])
def test_model_think_defaults_to_medium(tmp_path: Path, command: str) -> None:
    runner = CliRunner()
    with (
        patch("archivatorium.cli.MetadataProcessor") as metadata_processor,
        patch("archivatorium.cli.TaggingService"),
        patch("archivatorium.cli.OllamaClient"),
        patch("archivatorium.ocr_engine.OCREngine") as ocr_engine,
    ):
        metadata_processor.return_value.get_files.return_value = []
        args = _metadata_args(tmp_path) if command == "metadata" else _ocr_args(tmp_path)
        result = runner.invoke(cli, args)

    assert result.exit_code == 0, result.output
    boundary = metadata_processor if command == "metadata" else ocr_engine
    assert boundary.call_args.kwargs["model_think"] == "medium"


@pytest.mark.parametrize("command", ["metadata", "ocr"])
def test_model_think_help_lists_choices_and_default(command: str) -> None:
    result = CliRunner().invoke(cli, [command, "--help"])
    normalized_help = " ".join(result.output.lower().split())

    assert result.exit_code == 0
    assert "--model-think" in result.output
    assert "false" in normalized_help
    assert "low" in normalized_help
    assert "medium" in normalized_help
    assert "high" in normalized_help
    assert "default: medium" in normalized_help


@pytest.mark.parametrize("command", ["metadata", "ocr"])
def test_invalid_model_think_is_rejected_before_processing(tmp_path: Path, command: str) -> None:
    runner = CliRunner()
    with (
        patch("archivatorium.cli.MetadataProcessor") as metadata_processor,
        patch("archivatorium.ocr_engine.OCREngine") as ocr_engine,
    ):
        args = (
            _metadata_args(tmp_path, "extreme")
            if command == "metadata"
            else _ocr_args(tmp_path, "extreme")
        )
        result = runner.invoke(cli, args)

    assert result.exit_code == 2
    assert "invalid value" in result.output.lower()
    assert "false" in result.output.lower()
    assert "low" in result.output.lower()
    assert "medium" in result.output.lower()
    assert "high" in result.output.lower()
    metadata_processor.assert_not_called()
    ocr_engine.assert_not_called()
