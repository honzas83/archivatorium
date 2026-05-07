from unittest.mock import patch
from click.testing import CliRunner
from ocrpolish.cli import cli
from ocrpolish.models.metadata import MetadataSchema
from tests.unit.test_ollama_client import create_mock_ollama_response

def test_full_bibtex_citation_output(tmp_path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    (input_dir / "doc1.md").write_text("Test content for citation.")
    
    output_dir = tmp_path / "output"
    
    runner = CliRunner()
    
    mock_metadata = {
        "title": "Nuclear Planning Group",
        "author_name": "E. F. Luff",
        "date": "1973-10-05",
        "archive_code": "NPG-D-73-10",
        "author_institution": "NATO",
    }
    
    with patch("ollama.Client.chat") as mock_chat:
        mock_chat.return_value = create_mock_ollama_response(
            MetadataSchema(**mock_metadata).model_dump_json()
        )
        
        # Mock date.today() to have consistent output if needed, 
        # but here we mostly care about the BibTeX fields we provided.
        result = runner.invoke(cli, ["metadata", str(input_dir), str(output_dir)])
        
        assert result.exit_code == 0
        
        output_file = output_dir / "doc1.md"
        assert output_file.exists()
        content = output_file.read_text()
        
        # Verify BibTeX block structure and fields
        assert "@misc{NPG-D-73-10," in content
        assert "author = {Luff, E. F.}," in content
        assert "title = {Nuclear Planning Group}," in content
        assert "date = {1973-10-05}," in content
        assert "note = {NATO, NPG-D-73-10, NATO Archive Obsidian}," in content
