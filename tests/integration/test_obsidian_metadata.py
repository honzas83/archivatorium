from pathlib import Path
from typing import Any
from unittest.mock import patch

from click.testing import CliRunner

from ocrpolish.cli import cli
from ocrpolish.data_model import TAG_PREFIX_ENTITY
from ocrpolish.models.metadata import MetadataSchema
from ocrpolish.utils.metadata import parse_frontmatter


def create_mock_ollama_response(content: str) -> dict[str, dict[str, str]]:
    return {
        "message": {
            "role": "assistant",
            "content": content
        }
    }

@patch("ollama.Client.chat")
def test_obsidian_metadata_standard(mock_chat: Any, tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    input_file = input_dir / "test.md"
    input_file.write_text("Test content", encoding="utf-8")
    
    mock_metadata = {
        "title": "Document Title",
        "summary": "Concise summary.",
        "abstract": "Detailed abstract.",
        "author_name": "John Doe",
        "date": "2026-01-01"
    }
    
    mock_chat.return_value = create_mock_ollama_response(
        MetadataSchema(**mock_metadata).model_dump_json()
    )
    
    runner = CliRunner()
    result = runner.invoke(cli, ["metadata", str(input_dir), str(output_dir)])
    assert result.exit_code == 0
    
    output_file = output_dir / "test.md"
    assert output_file.exists()
    content = output_file.read_text()
    
    metadata, body = parse_frontmatter(content)
    
    assert metadata["title"] == "Document Title"
    assert metadata["summary"] == "Concise summary."
    assert "abstract" not in metadata
    assert metadata["author_name"] == "John Doe"
    assert metadata["date"] == "2026-01-01"
    
    assert "> [!abstract]" in body
    assert "# Document Title" in body
    assert "Detailed abstract." in body

def test_obsidian_metadata_entities(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    input_file = input_dir / "test.md"
    input_file.write_text("Test content", encoding="utf-8")
    
    mock_metadata = {
        "title": "Entity Test",
        "mentioned_states": ["United Kingdom", "United States"],
        "mentioned_organisations": ["NATO"],
        "mentioned_cities": ["London, United Kingdom", "Washington, United States"],
        "location_state": "Germany"
    }
    
    runner = CliRunner()
    with patch("ollama.Client.chat") as mock_chat:
        mock_chat.return_value = create_mock_ollama_response(
            MetadataSchema(**mock_metadata).model_dump_json()
        )
        
        result = runner.invoke(cli, ["metadata", str(input_dir), str(output_dir)])
        assert result.exit_code == 0
        
        output_file = output_dir / "test.md"
        content = output_file.read_text()
        metadata, body = parse_frontmatter(content)
        
        # Excluded from frontmatter
        assert "mentioned_states" not in metadata
        assert "mentioned_organisations" not in metadata
        assert "mentioned_cities" not in metadata
        
        # Present in body callout
        assert "## Entities" in body
        assert "* States" in body
        assert f"  - #{TAG_PREFIX_ENTITY}/State/United-Kingdom" in body
        assert f"  - #{TAG_PREFIX_ENTITY}/State/United-States" in body
        assert "* Organisations" in body
        assert f"  - #{TAG_PREFIX_ENTITY}/Org/NATO" in body
        assert "* Cities" in body
        assert f"  - #{TAG_PREFIX_ENTITY}/City/United-Kingdom/London" in body
        assert f"  - #{TAG_PREFIX_ENTITY}/City/United-States/Washington" in body

