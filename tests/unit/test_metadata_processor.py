from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from ocrpolish.data_model import TAG_PREFIX_TOPIC
from ocrpolish.processor_metadata import MetadataProcessor
from ocrpolish.utils.metadata import parse_frontmatter


@pytest.fixture
def mock_ollama() -> MagicMock:
    return MagicMock()


@pytest.fixture
def processor(mock_ollama: MagicMock, tmp_path: Path) -> MetadataProcessor:
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return MetadataProcessor(mock_ollama, output_dir)


def test_prepare_obsidian_metadata_removes_empty_fields(processor: Any) -> None:
    raw_dict: dict[str, Any] = {
        "title": "Test Title",
        "summary": "One sentence.",
        "author_name": "",
        "date": None,
        "tags": [],
        "language": "English",
    }
    input_file = Path("test.md")
    output_file = processor.output_dir / "test.md"

    # We need to mock _get_pdf_link because it's called in _prepare_obsidian_metadata
    processor._get_pdf_link = MagicMock(return_value="[[test.pdf]]")

    metadata = processor._prepare_obsidian_metadata(raw_dict, input_file, output_file)

    assert "title" in metadata
    assert "summary" in metadata
    assert "language" in metadata
    assert "source" in metadata  # Added by the processor

    # Empty/None/Empty list should be removed
    assert "author_name" not in metadata
    assert "date" not in metadata
    assert "tags" not in metadata


def test_prepare_obsidian_metadata_field_order_and_exclusion(processor: Any) -> None:
    raw_dict: dict[str, Any] = {
        "title": "Document Title",
        "summary": "This is a summary.",
        "sender": "Alice",
        "recipient": "Bob",
        "intent": "Some action",
        "mentioned_states": ["UK"],
        "mentioned_organisations": ["NATO"],
        "mentioned_cities": ["London"],
        "date": "2024-04-30",
        "author_name": "Author",
        "pages": 10,  # Manually added before calling _prepare
    }
    input_file = Path("doc.md")
    output_file = processor.output_dir / "doc.md"
    processor._get_pdf_link = MagicMock(return_value="[[doc.pdf]]")

    metadata = processor._prepare_obsidian_metadata(raw_dict, input_file, output_file)

    # Check for renaming and presence
    assert "intent" in metadata
    assert metadata["intent"] == "Some action"
    assert "pages" in metadata

    # Check for exclusion of mentioned_*
    assert "mentioned_states" not in metadata
    assert "mentioned_organisations" not in metadata
    assert "mentioned_cities" not in metadata

    # Check for order (summary, pages, sender, recipient, intent)
    keys = list(metadata.keys())
    # title is first in primary_keys
    assert keys[0] == "title"
    assert keys[1] == "summary"
    assert keys[2] == "pages"
    assert keys[3] == "sender"
    assert keys[4] == "recipient"
    assert keys[5] == "intent"


def test_process_file_english_consistency(processor: Any, tmp_path: Path) -> None:
    input_file = tmp_path / "french.md"
    # Even if content is French, prompt mandates English
    input_file.write_text("C'est un document en français.")
    output_file = tmp_path / "output.md"

    # Mock Ollama response (simulating LLM following English instruction)
    mock_metadata = MagicMock()
    mock_metadata.title = "French Document"
    mock_metadata.summary = "This is a document in French."
    mock_metadata.language = "English"  # Mandated English
    mock_metadata.model_dump.return_value = {
        "title": "French Document",
        "summary": "This is a document in French.",
        "language": "English",
    }
    processor.client.extract_structured.return_value = mock_metadata
    processor._get_pdf_link = MagicMock(return_value="[[french.pdf]]")

    processor.process_file(input_file, output_file)

    content = output_file.read_text()
    metadata, body = parse_frontmatter(content)

    assert metadata["title"] == "French Document"
    assert metadata["language"] == "English"


def test_process_file_callout_presence_and_normalization(processor: Any, tmp_path: Path) -> None:
    input_file = tmp_path / "test_callouts.md"
    input_file.write_text("This is the main body of the document.")
    output_file = tmp_path / "output_callouts.md"

    # Mock Ollama response
    mock_metadata = MagicMock()
    mock_metadata.title = "Callout Test"
    mock_metadata.summary = "A document testing callouts."
    mock_metadata.abstract = "This is a detailed abstract."
    mock_metadata.date = "2026-05-07"
    mock_metadata.archive_code = "ABC-123"
    mock_metadata.tags = ["tag1"]
    mock_metadata.model_dump.return_value = {
        "title": "Callout Test",
        "summary": "A document testing callouts.",
        "abstract": "This is a detailed abstract.",
        "date": "2026-05-07",
        "archive_code": "ABC-123",
        "tags": ["tag1"],
    }
    processor.client.extract_structured.return_value = mock_metadata
    processor._get_pdf_link = MagicMock(return_value="[[test.pdf]]")

    # Mock tagging service
    mock_tagging_result = MagicMock()
    mock_topic = MagicMock()
    mock_topic.topic = "TestTopic"
    mock_topic.reason = "Justified by 'direct citation' from text."
    mock_tagging_result.topic_tags = [mock_topic]
    mock_tagging_result.entity_tags = ["Entity1"]
    mock_tagging_result.conceptual_tags = ["Concept1"]

    processor.tagging_service = MagicMock()
    processor.tagging_service.extract_tags.return_value = mock_tagging_result

    processor.process_file(input_file, output_file)

    content = output_file.read_text()

    # Check for Metadata callout
    assert "> [!info] Metadata" in content
    assert "≡&nbsp;**title**:" in content

    # Check for Abstract callout
    assert "> [!abstract]" in content
    assert "This is a detailed abstract." in content

    # Check for normalized citation in topic reason
    # 'direct citation' should become _"direct citation"_
    assert f'#{TAG_PREFIX_TOPIC}/TestTopic — Justified by _"direct citation"_ from text.' in content

    # Check for Citing callout
    assert "> [!citing this document]" in content
    assert "date = {2026-05-07}" in content
