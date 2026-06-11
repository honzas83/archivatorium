from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from ocrpolish.cli import cli


@pytest.fixture
def temp_ocr_dirs(tmp_path: Path) -> tuple[Path, Path]:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()

    # Create a dummy pdf
    pdf_file = input_dir / "test.pdf"
    pdf_file.write_text("dummy pdf content")
    return input_dir, output_dir


def test_ocr_command_basic(temp_ocr_dirs: tuple[Path, Path]) -> None:
    input_dir, output_dir = temp_ocr_dirs
    runner = CliRunner()

    with (
        patch("ocrpolish.ocr_engine.PdfReader") as mock_reader_class,
        patch("ocrpolish.ocr_engine.convert_from_path") as mock_convert,
        patch("ocrpolish.ocr_engine.Client") as mock_client_class,
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
