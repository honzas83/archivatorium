from unittest.mock import MagicMock

import pytest

from ocrpolish.data_model import TAG_PREFIX_ENTITY, TAG_PREFIX_TAG, TAG_PREFIX_TOPIC
from ocrpolish.models.metadata import AggregatedTaggingResult, MetadataSchema
from ocrpolish.processor_metadata import MetadataProcessor
from ocrpolish.services.tagging_service import TaggingService


@pytest.fixture
def mock_ollama():
    return MagicMock()


@pytest.fixture
def mock_tagging_service():
    return MagicMock(spec=TaggingService)


def test_two_pass_tagging_output(tmp_path, mock_ollama, mock_tagging_service):
    # Setup directories
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    input_file = input_dir / "test_doc.md"
    input_file.write_text("This is the original document body.\n", encoding="utf-8")

    # Mock Step 1 extraction
    mock_metadata = MetadataSchema(
        title="Test Title",
        summary="Test Summary",
        abstract="Test Abstract",
        date="2026-01-01",
        mentioned_states=[],
        mentioned_organisations=[],
        mentioned_cities=[],
        tags=[],  # Should be empty or ignored in favor of step 2
    )
    mock_ollama.extract_structured.return_value = mock_metadata

    # Mock Step 2 Tagging extraction
    from ocrpolish.models.metadata import TopicResult

    mock_tagging_result = AggregatedTaggingResult(
        conceptual_tags=["#NATO", "#Exercise"],
        entity_tags=["State/UK", "Org/NATO"],
        topic_tags=[
            TopicResult(topic="Category/Military/Training", reason="Training exercises mentioned")
        ],
    )
    mock_tagging_service.extract_tags.return_value = mock_tagging_result

    processor = MetadataProcessor(
        ollama_client=mock_ollama, output_dir=output_dir, tagging_service=mock_tagging_service
    )

    processor.process_file(input_file, output_dir / "test_doc.md")

    output_file = output_dir / "test_doc.md"
    assert output_file.exists()

    content = output_file.read_text(encoding="utf-8")

    # Assert callout contains the expected sections from Step 2
    assert "## Categories/Topics" in content
    assert (
        f"- #{TAG_PREFIX_TOPIC}/Category/Military/Training — Training exercises mentioned"
        in content
    )

    assert "## Entities" in content
    assert f"  - #{TAG_PREFIX_ENTITY}/Org/NATO" in content
    assert f"  - #{TAG_PREFIX_ENTITY}/State/UK" in content

    assert "## Tags" in content
    assert f"#{TAG_PREFIX_TAG}/NATO" in content
    assert f"#{TAG_PREFIX_TAG}/Exercise" in content

    assert f"#{TAG_PREFIX_TAG}/NATO #{TAG_PREFIX_TAG}/Exercise" in content

    mock_tagging_service.extract_tags.assert_called_once()


def test_two_pass_tagging_output_retains_more_than_ten_topics(
    tmp_path, mock_ollama, mock_tagging_service
):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    input_file = input_dir / "dense_doc.md"
    input_file.write_text("NATO dense substantive document body.\n", encoding="utf-8")
    mock_ollama.extract_structured.return_value = MetadataSchema(
        title="Dense Doc",
        summary="Dense Summary",
        abstract="Dense Abstract",
        date="2026-01-01",
        mentioned_states=[],
        mentioned_organisations=[],
        mentioned_cities=[],
        tags=[],
    )

    from ocrpolish.models.metadata import TopicResult

    mock_tagging_service.extract_tags.return_value = AggregatedTaggingResult(
        conceptual_tags=["#NATO", "#Exercise", "#Consultation"],
        entity_tags=["Org/NATO"],
        topic_tags=[
            TopicResult(topic=f"Category/Topic-{idx}", reason=f"Reason {idx}") for idx in range(12)
        ],
    )

    processor = MetadataProcessor(
        ollama_client=mock_ollama,
        output_dir=output_dir,
        tagging_service=mock_tagging_service,
    )

    processor.process_file(input_file, output_dir / "dense_doc.md")

    content = (output_dir / "dense_doc.md").read_text(encoding="utf-8")
    for idx in range(12):
        assert f"- #{TAG_PREFIX_TOPIC}/Category/Topic-{idx} — Reason {idx}" in content
