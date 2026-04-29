from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from ocrpolish.cli import cli


@pytest.fixture
def input_dir(tmp_path):
    d = tmp_path / "input"
    d.mkdir()
    f = d / "test.md"
    f.write_text("This is a document about nuclear deterrence strategies and NATO.")
    return d

@pytest.fixture
def hierarchy_file(tmp_path):
    content = """
categories:
  - category: "Doctrine and Strategy"
    topics:
      - topic: "Nuclear Deterrence"
        description: "Preventing aggression through threat."
        positive_samples: "deterrence theory"
"""
    p = tmp_path / "hierarchy.yaml"
    p.write_text(content)
    return p

@patch("ocrpolish.services.ollama_client.OllamaClient.extract_structured")
def test_cli_flat_topics_integration(mock_extract, input_dir, hierarchy_file, tmp_path):
    output_dir = tmp_path / "output"
    
    # Mock responses for MetadataSchema and FlatTopicSelectionSchema
    # First call is for MetadataSchema (Pass 1)
    # Second call is for FlatTopicSelectionSchema (Topic Extraction)
    
    mock_metadata = MagicMock()
    mock_metadata.title = "Test Title"
    mock_metadata.abstract = "Test Abstract"
    mock_metadata.tags = ["test"]
    mock_metadata.model_dump.return_value = {
        "title": "Test Title",
        "abstract": "Test Abstract",
        "tags": ["test"]
    }
    
    mock_topic_assignment = MagicMock()
    mock_topic_assignment.topic_id = "Doctrine and Strategy/Nuclear Deterrence"
    mock_topic_assignment.reason = "Matches nuclear deterrence context."
    
    mock_topic_selection = MagicMock()
    mock_topic_selection.assignments = [mock_topic_assignment]
    
    mock_extract.side_effect = [mock_metadata, mock_topic_selection]
    
    runner = CliRunner()
    result = runner.invoke(cli, [
        "metadata",
        str(input_dir),
        str(output_dir),
        "--hierarchy-file", str(hierarchy_file),
        "--flat-topics"
    ])
    
    assert result.exit_code == 0
    
    output_file = output_dir / "test.md"
    assert output_file.exists()
    content = output_file.read_text()
    
    # Verify hierarchical tag and reason are present in the output
    assert "#Doctrine-and-Strategy/Nuclear-Deterrence" in content
    assert "Matches nuclear deterrence context." in content
