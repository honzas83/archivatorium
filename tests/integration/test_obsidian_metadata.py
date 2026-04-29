from unittest.mock import patch

import pytest
from click.testing import CliRunner

from ocrpolish.cli import cli
from ocrpolish.models.metadata import MetadataSchema
from ocrpolish.utils.metadata import parse_frontmatter
from tests.unit.test_ollama_client import create_mock_ollama_response


@pytest.fixture
def temp_dirs(tmp_path):
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    vault_root = tmp_path / "vault"
    input_dir.mkdir()
    output_dir.mkdir()
    vault_root.mkdir()
    
    # Create a dummy markdown file
    md_file = input_dir / "test.md"
    md_file.write_text("This is a test document.")
    
    return input_dir, output_dir, vault_root

def test_obsidian_metadata_flattening(temp_dirs):
    input_dir, output_dir, _ = temp_dirs
    runner = CliRunner()
    
    # Mock data with "nested" fields as extracted by the LLM
    # Note: MetadataSchema in ocrpolish/models/metadata.py actually has 
    # flattened fields like correspondence_sender, but the logic in 
    # processor_metadata.py currently wraps them in a 'correspondence' dict.
    mock_metadata = {
        "title": "Flattened Test",
        "correspondence_sender": "Sender Name",
        "correspondence_recipient": "Recipient Name",
        "correspondence_transaction": "Requesting Info",
        "tags": ["#NATO", "#Security"]
    }
    
    with patch("ollama.Client.chat") as mock_chat:
        mock_chat.return_value = create_mock_ollama_response(
            MetadataSchema(**mock_metadata).model_dump_json()
        )
        
        result = runner.invoke(cli, ["metadata", str(input_dir), str(output_dir)])
        assert result.exit_code == 0
        
        output_file = output_dir / "test.md"
        assert output_file.exists()
        
        content = output_file.read_text()
        metadata, body = parse_frontmatter(content)
        
        # Verify flattening: NO 'correspondence' dict, but top-level keys
        assert "correspondence" not in metadata
        assert metadata["correspondence_sender"] == "Sender Name"
        assert metadata["correspondence_recipient"] == "Recipient Name"
        
        # Tags should be cleaned (Task T015/T016, but testing early)
        assert "NATO" in metadata["tags"]
        assert "#NATO" not in metadata["tags"]


def test_obsidian_metadata_relative_source(temp_dirs):
    input_dir, output_dir, vault_root = temp_dirs
    runner = CliRunner()
    
    # Place input file deep in vault
    # vault/Notes/Research/test.md
    notes_dir = vault_root / "Notes" / "Research"
    notes_dir.mkdir(parents=True)
    md_file = notes_dir / "test.md"
    md_file.write_text("Content")
    
    # Assume PDF is in vault/Attachments/test.pdf
    attach_dir = vault_root / "Attachments"
    attach_dir.mkdir()
    # (We don't actually need the PDF file to exist for the metadata extraction to work, 
    # but the processor will calculate the path based on vault_root and pdf_dir)
    
    mock_metadata = {"title": "Path Test"}
    
    with patch("ollama.Client.chat") as mock_chat:
        mock_chat.return_value = create_mock_ollama_response(
            MetadataSchema(**mock_metadata).model_dump_json()
        )
        
        # Run with --vault-root and --pdf-dir
        result = runner.invoke(cli, [
            "metadata", 
            str(notes_dir), 
            str(output_dir), 
            "--vault-root", str(vault_root),
            "--pdf-dir", str(attach_dir)
        ])
        assert result.exit_code == 0
        
        output_file = output_dir / "test.md"
        assert output_file.exists()
        
        content = output_file.read_text()
        metadata, _ = parse_frontmatter(content)
        
        # Expected relative path from vault root to PDF is Attachments/test.pdf
        assert metadata["source"] == "[[Attachments/test.pdf]]"


def test_obsidian_metadata_tags(temp_dirs):
    input_dir, output_dir, _ = temp_dirs
    runner = CliRunner()
    
    mock_metadata = {
        "title": "Tag Test",
        "tags": ["#NATO", " #Security ", "Cold War"]
    }
    
    with patch("ollama.Client.chat") as mock_chat:
        mock_chat.return_value = create_mock_ollama_response(
            MetadataSchema(**mock_metadata).model_dump_json()
        )
        
        result = runner.invoke(cli, ["metadata", str(input_dir), str(output_dir)])
        assert result.exit_code == 0
        
        output_file = output_dir / "test.md"
        content = output_file.read_text()
        metadata, _ = parse_frontmatter(content)
        
        # Tags should be: ["NATO", "Security", "ColdWar"]
        assert metadata["tags"] == ["NATO", "Security", "ColdWar"]


def test_obsidian_metadata_abstract_callout(temp_dirs):
    input_dir, output_dir, _ = temp_dirs
    runner = CliRunner()
    
    mock_metadata = {
        "title": "Callout Test",
        "abstract": "This is a detailed abstract.\nIt has multiple lines."
    }
    
    with patch("ollama.Client.chat") as mock_chat:
        mock_chat.return_value = create_mock_ollama_response(
            MetadataSchema(**mock_metadata).model_dump_json()
        )
        
        result = runner.invoke(cli, ["metadata", str(input_dir), str(output_dir)])
        assert result.exit_code == 0
        
        output_file = output_dir / "test.md"
        content = output_file.read_text()
        
        # Verify callout is present in the body (after frontmatter)
        assert "> [!abstract] Abstract" in content
        assert "> This is a detailed abstract." in content
        assert "> It has multiple lines." in content
        
        # Verify it's BEFORE the original content
        _, body = parse_frontmatter(content)
        assert body.startswith("> [!abstract] Abstract")
        assert "This is a test document." in body
