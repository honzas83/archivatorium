from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open

import pytest
from ocrpolish.ocr_engine import OCREngine


@pytest.fixture
def mock_ollama_client():
    with patch("ocrpolish.ocr_engine.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        yield mock_client


@pytest.fixture
def mock_pdf_reader():
    with patch("ocrpolish.ocr_engine.PdfReader") as mock_reader_class:
        mock_reader = MagicMock()
        mock_reader.pages = [MagicMock(), MagicMock()]  # 2 pages
        mock_reader_class.return_value = mock_reader
        yield mock_reader


@pytest.fixture
def mock_convert_from_path():
    with patch("ocrpolish.ocr_engine.convert_from_path") as mock_convert:
        mock_image = MagicMock()
        mock_convert.return_value = [mock_image]
        yield mock_convert


def test_ocr_engine_init(mock_ollama_client):
    engine = OCREngine(host="http://mock-host", user="user", password="password")
    assert engine.host == "http://mock-host"
    assert engine.user == "user"
    assert engine.password == "password"
    assert engine.model == "qwen3.5:9b"
    assert engine.dpi == 300


def test_count_pdf_pages(mock_pdf_reader):
    engine = OCREngine()
    with patch("builtins.open", mock_open(read_data=b"dummy")):
        pages = engine.count_pdf_pages(Path("dummy.pdf"))
    assert pages == 2


def test_ocr_single_page_success(mock_ollama_client):
    engine = OCREngine()
    # Mock Ollama Client response
    mock_response = MagicMock()
    mock_response.message = {"content": "Transcription content"}
    mock_ollama_client.chat.return_value = mock_response

    transcription = engine.ocr_single_page(
        image_path=Path("dummy.png"), last_text="previous page text"
    )
    assert transcription == "Transcription content"
    mock_ollama_client.chat.assert_called_once()


def test_ocr_single_page_retry_success(mock_ollama_client):
    engine = OCREngine()
    mock_response = MagicMock()
    mock_response.message = {"content": "Successful after retry"}

    # Fail once, then succeed
    mock_ollama_client.chat.side_effect = [Exception("Temporary error"), mock_response]

    transcription = engine.ocr_single_page(
        image_path=Path("dummy.png"), retry=2, retry_backoff=0.01
    )
    assert transcription == "Successful after retry"
    assert mock_ollama_client.chat.call_count == 2


def test_run_ocr(mock_pdf_reader, mock_convert_from_path, mock_ollama_client):
    engine = OCREngine()
    mock_response = MagicMock()
    mock_response.message = {"content": "Page content here"}
    mock_ollama_client.chat.return_value = mock_response

    with (
        patch("builtins.open", mock_open(read_data=b"dummy")),
        patch("pathlib.Path.unlink"),
    ):
        result = engine.run_ocr(
            input_pdf=Path("dummy.pdf"),
            page_header=True,
        )

        assert "Page 1" in result
        assert "Page 2" in result
        assert "Page content here" in result
        assert mock_ollama_client.chat.call_count == 2


def test_run_ocr_resume(mock_pdf_reader, mock_convert_from_path, mock_ollama_client, tmp_path):
    engine = OCREngine()

    # Pre-create output md with page 1 already recognized
    output_md = tmp_path / "output.md"
    output_md.write_text("---\n\n# Page 1\n\nExisting content of page 1\n")

    mock_response = MagicMock()
    mock_response.message = {"content": "Page 2 content"}
    mock_ollama_client.chat.return_value = mock_response

    with (
        patch("builtins.open", mock_open(read_data=b"dummy")),
        patch("pathlib.Path.unlink"),
    ):
        engine.run_ocr(
            input_pdf=Path("dummy.pdf"),
            output_md=output_md,
            page_header=True,
        )

        # Chat should only be called once (for page 2), because page 1 is skipped
        assert mock_ollama_client.chat.call_count == 1

        # Verify call context contains previous page content
        call_args = mock_ollama_client.chat.call_args[1]
        user_message = call_args["messages"][-1]["content"]
        assert (
            "For OCR context, previous transcribed page was: Existing content of page 1"
            in user_message
        )

        # Verify output contains both pages
        output_content = output_md.read_text()
        assert "Page 1" in output_content
        assert "Existing content of page 1" in output_content
        assert "Page 2" in output_content
        assert "Page 2 content" in output_content
