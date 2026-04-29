from unittest.mock import patch

import pytest
from click.testing import CliRunner

from ocrpolish.cli import cli
from ocrpolish.models.metadata import LastDateSchema, MetadataSchema
from tests.unit.test_ollama_client import create_mock_ollama_response


@pytest.fixture
def temp_dirs(tmp_path):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    
    # Create a dummy markdown file
    md_file = input_dir / "test.md"
    md_file.write_text("This is a test document.")
    
    return input_dir, output_dir

def test_metadata_command_basic(temp_dirs):
    input_dir, output_dir = temp_dirs
    runner = CliRunner()
    
    mock_metadata = {
        "title": "Test Title",
        "author_name": "Test Author",
        "language": "English",
        "date": "1981-11-19"
    }
    
    with patch("ollama.Client.chat") as mock_chat:
        mock_chat.return_value = create_mock_ollama_response(
            MetadataSchema(**mock_metadata).model_dump_json()
        )
        
        result = runner.invoke(cli, ["metadata", str(input_dir), str(output_dir)])
        
        assert result.exit_code == 0
        
def test_metadata_command_large_file_date_fallback(temp_dirs):
    input_dir, output_dir = temp_dirs
    runner = CliRunner()
    
    # Create a large file (> 8000 chars)
    large_file = input_dir / "large.md"
    content = (
        "Start of document without clear date. " + 
        ("x" * 9000) + 
        " End of document. Final Date: 2026-12-31."
    )
    large_file.write_text(content)
    
    with patch("ollama.Client.chat") as mock_chat:
        # Mock first pass (MetadataSchema) - missing date
        data1 = {"language": "English", "title": "Large Doc"}
        resp1 = create_mock_ollama_response(MetadataSchema(**data1).model_dump_json())
        
        # Mock second pass (LastDateSchema) - finds date
        data2 = {"date": "2026-12-31"}
        resp2 = create_mock_ollama_response(LastDateSchema(**data2).model_dump_json())
        
        mock_chat.side_effect = [resp1, resp2]
        
        result = runner.invoke(cli, ["metadata", str(input_dir), str(output_dir)])
        
        assert result.exit_code == 0
        
        output_file = output_dir / "large.md"
        assert output_file.exists()
        output_content = output_file.read_text()
        
        # Verify date was updated from the second pass
        assert "date: '2026-12-31'" in output_content or "date: 2026-12-31" in output_content
