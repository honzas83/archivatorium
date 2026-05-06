import os
from pathlib import Path
from click.testing import CliRunner
from ocrpolish.cli import cli
from ocrpolish.utils.metadata import parse_frontmatter
from unittest.mock import patch
from ocrpolish.models.metadata import MetadataSchema
from tests.unit.test_ollama_client import create_mock_ollama_response

def test_mirroring_pdf_subdirectory(tmp_path):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    output_dir.mkdir()
    
    # Create source structure
    subfolder = input_dir / "project-a"
    subfolder.mkdir()
    
    md_file = subfolder / "notes.md"
    md_file.write_text("Markdown content")
    
    pdf_file = subfolder / "notes.pdf"
    pdf_file.write_bytes(b"PDF content")
    
    runner = CliRunner()
    
    mock_metadata = {
        "title": "Test Document",
        "summary": "Summary",
        "tags": ["test"]
    }

    with patch("ollama.Client.chat") as mock_chat:
        mock_chat.return_value = create_mock_ollama_response(
            MetadataSchema(**mock_metadata).model_dump_json()
        )

        result = runner.invoke(cli, ["metadata", str(input_dir), str(output_dir)])
        assert result.exit_code == 0
        
    # Verify PDF location
    expected_pdf = output_dir / "project-a" / "pdf" / "notes.pdf"
    assert expected_pdf.exists()
    
    # Verify MD link
    expected_md = output_dir / "project-a" / "notes.md"
    assert expected_md.exists()
    
    content = expected_md.read_text()
    metadata, body = parse_frontmatter(content)
    
    assert metadata["source"] == "[[pdf/notes.pdf]]"
