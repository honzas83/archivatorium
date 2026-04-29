import pytest
from unittest.mock import MagicMock
from ocrpolish.services.topics_service import TopicExtractor
from ocrpolish.services.ollama_client import OllamaClient

@pytest.fixture
def mock_ollama():
    return MagicMock(spec=OllamaClient)

@pytest.fixture
def hierarchy_file(tmp_path):
    content = """
categories:
  - category: "Cat1"
    topics:
      - topic: "Top1"
        description: "Desc1"
        positive_samples: "Pos1"
"""
    p = tmp_path / "hierarchy.yaml"
    p.write_text(content)
    return p

def test_generate_flat_topic_prompt(mock_ollama, hierarchy_file):
    extractor = TopicExtractor(mock_ollama, hierarchy_file, flat_mode=True)
    prompt = extractor._generate_flat_topic_prompt("Sample text")
    
    assert "Sample text" in prompt
    assert "TOPIC HIERARCHY (YAML):" in prompt
    assert "Cat1/Top1" in prompt
    assert "Desc1" in prompt
    assert "Pos1" in prompt

def test_extract_topics_flat_mapping(mock_ollama, hierarchy_file):
    extractor = TopicExtractor(mock_ollama, hierarchy_file, flat_mode=True)
    
    # Mock LLM response
    mock_selection = MagicMock()
    mock_assignment = MagicMock()
    mock_assignment.topic_id = "Cat1/Top1"
    mock_assignment.reason = "Because reasons"
    mock_selection.assignments = [mock_assignment]
    
    mock_ollama.extract_structured.return_value = mock_selection
    
    results = extractor.extract_topics("Some text")
    
    assert len(results) == 1
    assert results[0].category == "Cat1"
    assert results[0].topic == "Top1"
    assert results[0].reason == "Because reasons"
