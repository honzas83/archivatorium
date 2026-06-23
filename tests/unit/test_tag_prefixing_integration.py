from unittest.mock import MagicMock

import pytest

from archivatorium.data_model import TAG_PREFIX_ENTITY, TAG_PREFIX_TAG, TAG_PREFIX_TOPIC
from archivatorium.models.metadata import AggregatedTaggingResult, TopicResult
from archivatorium.processor_metadata import MetadataProcessor


@pytest.fixture
def mock_ollama():
    return MagicMock()


@pytest.fixture
def processor(mock_ollama, tmp_path):
    output_dir = tmp_path / "output"
    return MetadataProcessor(ollama_client=mock_ollama, output_dir=output_dir)


def test_metadata_processor_prefixes(processor, tmp_path):
    input_file = tmp_path / "input.md"
    input_file.write_text("Some document content")
    output_file = processor.output_dir / "input.md"

    # Mock TaggingService result
    mock_tagging_result = AggregatedTaggingResult(
        conceptual_tags=["Reforger"],
        entity_tags=["State/United-Kingdom", "Org/NATO"],
        topic_tags=[TopicResult(topic="Strategy/Deterrence", reason="Test reason")],
    )

    processor.tagging_service = MagicMock()
    processor.tagging_service.extract_tags.return_value = mock_tagging_result

    # Mock extract_structured for the primary extraction
    mock_metadata = MagicMock()
    mock_metadata.tags = []
    mock_metadata.mentioned_states = []
    mock_metadata.mentioned_organisations = []
    mock_metadata.mentioned_cities = []
    mock_metadata.model_dump.return_value = {
        "title": "Test Document",
        "abstract": "Test Abstract",
        "date": "2026-05-20",
    }
    processor.client.extract_structured.return_value = mock_metadata

    processor.process_file(input_file, output_file)

    content = output_file.read_text()

    # Check for new prefixes in the abstract callout using global constants
    assert f"#{TAG_PREFIX_TOPIC}/Strategy/Deterrence" in content
    assert f"#{TAG_PREFIX_ENTITY}/State/United-Kingdom" in content
    assert f"#{TAG_PREFIX_ENTITY}/Org/NATO" in content
    assert f"#{TAG_PREFIX_TAG}/Reforger" in content


def test_metadata_processor_fallback_prefixes(processor, tmp_path):
    input_file = tmp_path / "input.md"
    input_file.write_text("Some document content")
    output_file = processor.output_dir / "input.md"

    # No tagging_service -> No fallback should happen anymore.
    processor.tagging_service = None

    # Mock extract_structured for the primary extraction
    mock_metadata = MagicMock()
    mock_metadata.model_dump.return_value = {
        "title": "Test Document",
        "abstract": "Test Abstract",
        "date": "2026-05-20",
    }
    processor.client.extract_structured.return_value = mock_metadata

    processor.process_file(input_file, output_file)

    content = output_file.read_text()

    # Check that tags, entities, and topics sections are not added
    assert "## Categories/Topics" not in content
    assert "## Entities" not in content
    assert "## Tags" not in content
