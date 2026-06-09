from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from ocrpolish.data_model import TAG_PREFIX_TOPIC
from ocrpolish.models.metadata import AggregatedTaggingResult, TopicResult
from ocrpolish.processor_metadata import MetadataProcessor
from ocrpolish.utils.metadata import is_generated_document_markdown, parse_frontmatter


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


def test_read_and_parse_source_stage(processor: Any, tmp_path: Path) -> None:
    input_file = tmp_path / "source.md"
    input_file.write_text(
        """---
title: Existing
---
> [!info] Metadata
> old

Clean body
""",
        encoding="utf-8",
    )

    raw = processor._read_source(input_file)
    parsed = processor._parse_source_and_strip_generated_sections(raw)

    assert parsed.raw_content == raw
    assert parsed.existing_metadata["title"] == "Existing"
    assert "Clean body" in parsed.cleaned_content
    assert "[!info] Metadata" not in parsed.cleaned_content


def test_generated_document_eligibility_excludes_support_files(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    vault.mkdir()
    eligible = vault / "document.md"
    eligible.write_text("body")
    excluded = [
        vault / "Index - Tags.md",
        vault / "index.md",
        vault / "document.filtered.md",
        vault / ".obsidian" / "support.md",
        vault / "templates" / "template.md",
    ]
    for path in excluded:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("support")

    assert is_generated_document_markdown(eligible, vault_root=vault)
    assert all(not is_generated_document_markdown(path, vault_root=vault) for path in excluded)


def test_extract_document_metadata_stage_adds_page_count(processor: Any) -> None:
    mock_metadata = MagicMock()
    mock_metadata.model_dump.return_value = {"title": "Doc", "date": "1981-01-01"}
    processor.client.extract_structured.return_value = mock_metadata

    extracted = processor._extract_document_metadata(Path("doc.md"), "# Page 1\nText\n# Page 2")

    assert extracted.raw_dict["title"] == "Doc"
    assert extracted.raw_dict["pages"] == 2


def test_generated_tag_stage_formats_topics_entities_and_tags(processor: Any) -> None:
    tagging_result = AggregatedTaggingResult(
        conceptual_tags=["NATO"],
        entity_tags=["Org/NATO"],
        topic_tags=[TopicResult(topic="Cat/Top", reason="Because 'quote'.")],
    )
    processor.tagging_service = MagicMock()
    processor.tagging_service.extract_tags.return_value = tagging_result

    sections = processor._extract_generated_tags("document body")

    assert sections.topic_items == [f'- #{TAG_PREFIX_TOPIC}/Cat/Top — Because _"quote"_.']
    assert "#Entities/Org/NATO" in sections.entity_tags
    assert "#Tags/NATO" in sections.conceptual_tags
    assert "* Organisations" in sections.entity_section_body


def test_render_frontmatter_and_callout_stages(processor: Any) -> None:
    metadata = {
        "title": "Doc Title",
        "summary": "Summary.",
        "abstract": "Abstract body.",
        "date": "1981-01-01",
    }
    tag_sections = processor._format_generated_tags(
        AggregatedTaggingResult(conceptual_tags=["NATO"], entity_tags=[], topic_tags=[])
    )

    frontmatter = processor._render_frontmatter(metadata)
    callouts = processor._render_callouts(frontmatter, tag_sections, "# Doc Title\nBody")
    output = processor._assemble_output(frontmatter, callouts)

    assert "abstract" not in frontmatter.metadata
    assert "title: Doc Title" in frontmatter.frontmatter
    assert "> [!info] Metadata" in output
    assert "> [!abstract]" in output
    assert "Abstract body." in output
    assert "> [!citing this document]" in output
    assert output.index("> [!info] Metadata") < output.index("> [!abstract]")
    assert output.index("> [!abstract]") < output.index("> [!citing this document]")


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
