from unittest.mock import patch

import pytest
from click.testing import CliRunner

from archivatorium.cli import cli
from archivatorium.data_model import TAG_PREFIX_TOPIC
from archivatorium.models.metadata import MetadataSchema, TopicResult, WindowTaggingResult


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


@patch("archivatorium.services.ollama_client.OllamaClient.extract_structured")
def test_cli_flat_topics_integration(
    mock_extract, input_dir, hierarchy_file, useful_tags_file, tmp_path
):
    output_dir = tmp_path / "output"

    # Mock responses for MetadataSchema and WindowTaggingResult

    mock_metadata = MetadataSchema(title="Test Title", abstract="Test Abstract", tags=["test"])

    mock_tagging_result = WindowTaggingResult(
        topic_tags=[
            TopicResult(
                topic="Doctrine and Strategy/Nuclear Deterrence",
                reason="Mention of nuclear strategy",
            )
        ],
        conceptual_tags=[
            "#NuclearDeterrence",
            "#NuclearPlanning",
            "#NATOStrategy",
            "#DeterrenceStrategy",
            "#OperationalDoctrine",
        ],
        entity_tags=["Org/NATO"],
    )

    mock_extract.side_effect = [mock_metadata, mock_tagging_result]

    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "metadata",
            str(input_dir),
            str(output_dir),
            "--hierarchy-file",
            str(hierarchy_file),
            "--tags-file",
            str(useful_tags_file),
        ],
    )

    assert result.exit_code == 0

    output_file = output_dir / "test.md"
    assert output_file.exists()
    content = output_file.read_text()

    # Verify hierarchical tag is present in the output with reasoning
    expected_topic = (
        f"- #{TAG_PREFIX_TOPIC}/Doctrine-and-Strategy/Nuclear-Deterrence "
        "— Mention of nuclear strategy"
    )
    assert expected_topic in content
