import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from ocrpolish.processor_metadata import MetadataProcessor


@pytest.fixture
def dummy_ollama_client() -> MagicMock:
    client = MagicMock()
    # Mock extract_structured to return dummy metadata
    mock_metadata = MagicMock()
    mock_metadata.model_dump.return_value = {
        "author_name": "Jane Smith",
        "title": "Secret Meeting Minutes",
        "date": "1970-10-25",
        "author_institution": "Pentagon",
        "archive_code": "SECRET-70-1",
        "tags": ["Meeting", "Secret"]
    }
    mock_metadata.tags = ["Meeting", "Secret"]
    client.extract_structured.return_value = mock_metadata
    return client

def test_metadata_processor_appends_citations(dummy_ollama_client: MagicMock) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        input_dir = Path(tmpdir) / "input"
        output_dir = Path(tmpdir) / "output"
        input_dir.mkdir()
        
        # Create a dummy markdown file
        test_file = input_dir / "SECRET-70-1.md"
        test_file.write_text("# Page 1\n\nThis is a secret document.\n", encoding="utf-8")
        
        processor = MetadataProcessor(
            ollama_client=dummy_ollama_client,
            output_dir=output_dir,
            overwrite=True
        )
        
        output_file = output_dir / "SECRET-70-1.md"
        result = processor.process_file(test_file, output_file)
        
        assert result is True
        assert output_file.exists()
        
        content = output_file.read_text(encoding="utf-8")
        
        # Verify citation callout is present at the end
        assert "> [!citing this document]" in content
        assert "> **Chicago**:" in content
        assert "> **Harvard**:" in content
        assert "> **BibTeX**:" in content
        assert "Smith, Jane" in content or "Jane, Smith" in content
        assert "SECRET-70-1" in content
