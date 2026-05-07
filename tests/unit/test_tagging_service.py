from pathlib import Path
from unittest.mock import MagicMock

import pytest

from ocrpolish.models.metadata import TopicResult, WindowTaggingResult
from ocrpolish.services.tagging_service import TaggingService


@pytest.fixture
def mock_ollama():
    return MagicMock()


@pytest.fixture
def mock_windowing():
    return MagicMock()


def test_extract_tags_single_pass(mock_ollama, mock_windowing):
    # Set context limit high to force single pass
    service = TaggingService(mock_ollama, mock_windowing, Path('dummy.yaml'), Path('dummy.yaml'), context_limit=1000)
    text = "Short text"

    # Mock single pass result
    mock_result = WindowTaggingResult(
        conceptual_tags=["#Tag1"], 
        entity_tags=["State/UK"], 
        topic_tags=[TopicResult(topic="Category/Topic1", reason="Test reason")]
    )
    mock_ollama.extract_structured.return_value = mock_result

    # Implementation should use estimate_tokens(text)
    # For now, we stub it or rely on the logic we're about to write
    result = service.extract_tags(text)

    # Conceptual tags are normalized (hyphenated, no #)
    assert "Tag1" in result.conceptual_tags
    assert "State/UK" in result.entity_tags
    assert result.topic_tags[0].topic == "Category/Topic1"
    assert result.topic_tags[0].reason == "Test reason"
    mock_ollama.extract_structured.assert_called_once()
    mock_windowing.get_windows.assert_not_called()


def test_extract_tags_sliding_window(mock_ollama, mock_windowing):
    # Set context limit low to force sliding window
    service = TaggingService(mock_ollama, mock_windowing, Path('dummy.yaml'), Path('dummy.yaml'), context_limit=5)
    text = "Very long text that exceeds limit"

    # Mock windowing
    mock_windowing.get_windows.return_value = ["chunk1", "chunk2"]

    # Mock results for each chunk
    mock_ollama.extract_structured.side_effect = [
        WindowTaggingResult(
            conceptual_tags=["#T1"], 
            entity_tags=["E1"], 
            topic_tags=[TopicResult(topic="Top1", reason="R1")]
        ),
        WindowTaggingResult(
            conceptual_tags=["#T2"], 
            entity_tags=["E2"], 
            topic_tags=[TopicResult(topic="Top2", reason="R2")]
        ),
    ]

    result = service.extract_tags(text)

    # Tags are normalized (hyphenated, no #)
    assert "T1" in result.conceptual_tags
    assert "T2" in result.conceptual_tags
    assert "E1" in result.entity_tags
    assert "E2" in result.entity_tags
    
    topics = {t.topic: t.reason for t in result.topic_tags}
    assert "Top1" in topics
    assert topics["Top1"] == "R1"
    assert "Top2" in topics
    assert topics["Top2"] == "R2"
    
    assert mock_ollama.extract_structured.call_count == 2
    mock_windowing.get_windows.assert_called_once_with(text)
