from collections.abc import Callable
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from archivatorium.cli import cli
from archivatorium.ocr_engine import FIRERED_USER_PROMPT, SYSTEM_PROMPT, USER_PROMPT


def test_ocr_command_basic(temp_ocr_dirs: tuple[Path, Path]) -> None:
    input_dir, output_dir = temp_ocr_dirs
    runner = CliRunner()

    with (
        patch("archivatorium.ocr_engine.PdfReader") as mock_reader_class,
        patch("archivatorium.ocr_engine.convert_from_path") as mock_convert,
        patch("archivatorium.ocr_engine.Client") as mock_client_class,
        patch("pathlib.Path.unlink"),
    ):
        # Setup mocks
        mock_reader = MagicMock()
        mock_reader.pages = [MagicMock()]  # 1 page
        mock_reader_class.return_value = mock_reader

        mock_convert.return_value = [MagicMock()]

        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.message = {"content": "Transcribed text for test.pdf"}
        mock_client.chat.return_value = mock_response
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            cli,
            [
                "ocr",
                str(input_dir),
                str(output_dir),
                "--model",
                "mock-model",
            ],
        )

        assert result.exit_code == 0

        output_md = output_dir / "test.md"
        assert output_md.exists()
        content = output_md.read_text()
        assert "Page 1" in content
        assert "Transcribed text for test.pdf" in content
        kwargs = mock_client.chat.call_args.kwargs
        assert kwargs["model"] == "mock-model"
        assert kwargs["messages"] == [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": USER_PROMPT,
                "images": [kwargs["messages"][-1]["images"][0]],
            },
        ]
        assert kwargs["options"] == {"num_ctx": 8192 * 3, "num_predict": 4096 * 4}
        assert "think" not in kwargs


def test_ocr_command_removes_reasoning_prefix_from_saved_markdown(
    temp_ocr_dirs: tuple[Path, Path],
) -> None:
    input_dir, output_dir = temp_ocr_dirs
    runner = CliRunner()

    with (
        patch("archivatorium.ocr_engine.PdfReader") as mock_reader_class,
        patch("archivatorium.ocr_engine.convert_from_path") as mock_convert,
        patch("archivatorium.ocr_engine.Client") as mock_client_class,
        patch("pathlib.Path.unlink"),
    ):
        mock_reader_class.return_value.pages = [MagicMock()]
        mock_convert.return_value = [MagicMock()]
        mock_response = MagicMock()
        mock_response.message = {
            "content": "private reasoning</think>\n\nRecognized archival text"
        }
        mock_client_class.return_value.chat.return_value = mock_response

        result = runner.invoke(cli, ["ocr", str(input_dir), str(output_dir)])

    assert result.exit_code == 0, result.output
    content = (output_dir / "test.md").read_text(encoding="utf-8")
    assert "Recognized archival text" in content
    assert "private reasoning" not in content
    assert "</think>" not in content


def test_ocr_command_removes_shared_margin_and_preserves_relative_indent(
    temp_ocr_dirs: tuple[Path, Path],
) -> None:
    input_dir, output_dir = temp_ocr_dirs
    runner = CliRunner()

    with (
        patch("archivatorium.ocr_engine.PdfReader") as mock_reader_class,
        patch("archivatorium.ocr_engine.convert_from_path") as mock_convert,
        patch("archivatorium.ocr_engine.Client") as mock_client_class,
        patch("pathlib.Path.unlink"),
    ):
        mock_reader_class.return_value.pages = [MagicMock()]
        mock_convert.return_value = [MagicMock()]
        mock_response = MagicMock()
        mock_response.message = {
            "content": "    First line\n        Nested line\n    Final line"
        }
        mock_client_class.return_value.chat.return_value = mock_response

        result = runner.invoke(cli, ["ocr", str(input_dir), str(output_dir)])

    assert result.exit_code == 0, result.output
    content = (output_dir / "test.md").read_text(encoding="utf-8")
    assert content.endswith("First line\n    Nested line\nFinal line")


def test_ocr_command_glm_mode(
    temp_ocr_dirs: tuple[Path, Path],
    ocr_response_factory: Callable[[str], MagicMock],
    ocr_call_kwargs: Callable[..., dict[str, Any]],
) -> None:
    input_dir, output_dir = temp_ocr_dirs
    runner = CliRunner()

    with (
        patch("archivatorium.ocr_engine.PdfReader") as mock_reader_class,
        patch("archivatorium.ocr_engine.convert_from_path") as mock_convert,
        patch("archivatorium.ocr_engine.Client") as mock_client_class,
        patch("pathlib.Path.unlink"),
    ):
        mock_reader = MagicMock()
        mock_reader.pages = [MagicMock()]
        mock_reader_class.return_value = mock_reader
        mock_convert.return_value = [MagicMock()]

        mock_client = MagicMock()
        mock_client.chat.return_value = ocr_response_factory("GLM transcription")
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            cli,
            [
                "ocr",
                "--mode",
                "glm",
                str(input_dir),
                str(output_dir),
            ],
        )

    assert result.exit_code == 0, result.output
    assert (output_dir / "test.md").read_text(encoding="utf-8").endswith("GLM transcription")
    kwargs = ocr_call_kwargs(mock_client)
    assert kwargs["model"] == "qwen3.5:9b"
    assert kwargs["messages"] == [
        {
            "role": "user",
            "content": "Text Recognition:",
            "images": [kwargs["messages"][0]["images"][0]],
        }
    ]
    assert kwargs["think"] is False
    assert kwargs["options"] == {
        "num_ctx": 8192 * 3,
        "temperature": 0.0,
        "top_p": 0.00001,
        "top_k": 1,
        "repeat_penalty": 1.1,
        "repeat_last_n": 512,
        "num_predict": 8192,
    }


def test_ocr_command_firered_mode_preserves_custom_model(
    temp_ocr_dirs: tuple[Path, Path],
    ocr_response_factory: Callable[[str], MagicMock],
    ocr_call_kwargs: Callable[..., dict[str, Any]],
) -> None:
    input_dir, output_dir = temp_ocr_dirs
    runner = CliRunner()

    with (
        patch("archivatorium.ocr_engine.PdfReader") as mock_reader_class,
        patch("archivatorium.ocr_engine.convert_from_path") as mock_convert,
        patch("archivatorium.ocr_engine.Client") as mock_client_class,
        patch("pathlib.Path.unlink"),
    ):
        mock_reader = MagicMock()
        mock_reader.pages = [MagicMock()]
        mock_reader_class.return_value = mock_reader
        mock_convert.return_value = [MagicMock()]
        mock_client = MagicMock()
        mock_client.chat.return_value = ocr_response_factory("FireRed transcription")
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            cli,
            [
                "ocr",
                "--mode",
                "firered",
                "--model",
                "remote/firered-ocr:latest",
                str(input_dir),
                str(output_dir),
            ],
        )

    assert result.exit_code == 0, result.output
    assert (output_dir / "test.md").read_text(encoding="utf-8").endswith("FireRed transcription")
    kwargs = ocr_call_kwargs(mock_client)
    assert kwargs == {
        "model": "remote/firered-ocr:latest",
        "messages": [
            {
                "role": "user",
                "content": FIRERED_USER_PROMPT,
                "images": [kwargs["messages"][0]["images"][0]],
            }
        ],
        "options": {"num_ctx": 8192 * 3, "num_predict": 4096 * 4},
        "stream": False,
    }


def test_ocr_command_explicit_standard_mode(
    temp_ocr_dirs: tuple[Path, Path],
    ocr_response_factory: Callable[[str], MagicMock],
) -> None:
    input_dir, output_dir = temp_ocr_dirs
    runner = CliRunner()

    with (
        patch("archivatorium.ocr_engine.PdfReader") as mock_reader_class,
        patch("archivatorium.ocr_engine.convert_from_path") as mock_convert,
        patch("archivatorium.ocr_engine.Client") as mock_client_class,
        patch("pathlib.Path.unlink"),
    ):
        mock_reader = MagicMock()
        mock_reader.pages = [MagicMock()]
        mock_reader_class.return_value = mock_reader
        mock_convert.return_value = [MagicMock()]
        mock_client = MagicMock()
        mock_client.chat.return_value = ocr_response_factory("Standard transcription")
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            cli,
            [
                "ocr",
                "--mode",
                "standard",
                str(input_dir),
                str(output_dir),
            ],
        )

    assert result.exit_code == 0, result.output
    assert "think" not in mock_client.chat.call_args.kwargs
    assert mock_client.chat.call_args.kwargs["messages"][0] == {
        "role": "system",
        "content": SYSTEM_PROMPT,
    }


def test_ocr_command_rejects_unsupported_mode_before_processing(
    temp_ocr_dirs: tuple[Path, Path],
) -> None:
    input_dir, output_dir = temp_ocr_dirs
    runner = CliRunner()

    with (
        patch("archivatorium.ocr_engine.Client") as mock_client_class,
        patch("archivatorium.ocr_engine.convert_from_path") as mock_convert,
    ):
        result = runner.invoke(
            cli,
            [
                "ocr",
                "--mode",
                "unsupported",
                str(input_dir),
                str(output_dir),
            ],
        )

    assert result.exit_code == 2
    assert "Invalid value for '--mode'" in result.output
    mock_client_class.assert_not_called()
    mock_convert.assert_not_called()


def test_ocr_command_glm_preserves_custom_model(
    temp_ocr_dirs: tuple[Path, Path],
    ocr_response_factory: Callable[[str], MagicMock],
) -> None:
    input_dir, output_dir = temp_ocr_dirs
    runner = CliRunner()

    with (
        patch("archivatorium.ocr_engine.PdfReader") as mock_reader_class,
        patch("archivatorium.ocr_engine.convert_from_path") as mock_convert,
        patch("archivatorium.ocr_engine.Client") as mock_client_class,
        patch("pathlib.Path.unlink"),
    ):
        mock_reader = MagicMock()
        mock_reader.pages = [MagicMock()]
        mock_reader_class.return_value = mock_reader
        mock_convert.return_value = [MagicMock()]
        mock_client = MagicMock()
        mock_client.chat.return_value = ocr_response_factory("Custom model text")
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            cli,
            [
                "ocr",
                "--mode",
                "glm",
                "--model",
                "remote/custom-glm:latest",
                str(input_dir),
                str(output_dir),
            ],
        )

    assert result.exit_code == 0, result.output
    kwargs = mock_client.chat.call_args.kwargs
    assert kwargs["model"] == "remote/custom-glm:latest"
    assert kwargs["messages"][0]["content"] == "Text Recognition:"
    assert kwargs["think"] is False


def test_ocr_command_propagates_all_inference_overrides(
    temp_ocr_dirs: tuple[Path, Path],
    ocr_response_factory: Callable[[str], MagicMock],
) -> None:
    input_dir, output_dir = temp_ocr_dirs
    runner = CliRunner()

    with (
        patch("archivatorium.ocr_engine.PdfReader") as mock_reader_class,
        patch("archivatorium.ocr_engine.convert_from_path") as mock_convert,
        patch("archivatorium.ocr_engine.Client") as mock_client_class,
        patch("pathlib.Path.unlink"),
    ):
        mock_reader = MagicMock()
        mock_reader.pages = [MagicMock()]
        mock_reader_class.return_value = mock_reader
        mock_convert.return_value = [MagicMock()]
        mock_client = MagicMock()
        mock_client.chat.return_value = ocr_response_factory("Overridden")
        mock_client_class.return_value = mock_client

        result = runner.invoke(
            cli,
            [
                "ocr",
                "--mode",
                "glm",
                "--temperature",
                "0",
                "--top-p",
                "0",
                "--top-k",
                "0",
                "--repeat-penalty",
                "1.2",
                "--repeat-last-n",
                "-1",
                "--num-predict",
                "-1",
                str(input_dir),
                str(output_dir),
            ],
        )

    assert result.exit_code == 0, result.output
    assert mock_client.chat.call_args.kwargs["options"] == {
        "num_ctx": 8192 * 3,
        "temperature": 0.0,
        "top_p": 0.0,
        "top_k": 0,
        "repeat_penalty": 1.2,
        "repeat_last_n": -1,
        "num_predict": -1,
    }


@pytest.mark.parametrize(
    ("option", "value"),
    [
        ("--temperature", "-0.1"),
        ("--top-p", "1.1"),
        ("--top-k", "-1"),
        ("--repeat-penalty", "0"),
        ("--repeat-last-n", "-2"),
        ("--num-predict", "0"),
    ],
)
def test_ocr_command_rejects_invalid_inference_before_processing(
    temp_ocr_dirs: tuple[Path, Path], option: str, value: str
) -> None:
    input_dir, output_dir = temp_ocr_dirs
    runner = CliRunner()

    with (
        patch("archivatorium.ocr_engine.Client") as mock_client_class,
        patch("archivatorium.ocr_engine.convert_from_path") as mock_convert,
    ):
        result = runner.invoke(
            cli,
            ["ocr", option, value, str(input_dir), str(output_dir)],
        )

    assert result.exit_code == 2
    assert "Invalid value" in result.output
    mock_client_class.assert_not_called()
    mock_convert.assert_not_called()
