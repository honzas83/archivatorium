from unittest.mock import MagicMock

from ocrpolish.processor_metadata import MetadataProcessor
from ocrpolish.utils.files import scan_files


def test_scan_files_excludes_filtered(tmp_path):
    # Setup files
    (tmp_path / "normal.md").write_text("content")
    (tmp_path / "extra.filtered.md").write_text("filtered content")
    (tmp_path / "subdir").mkdir()
    (tmp_path / "subdir" / "other.md").write_text("other content")
    (tmp_path / "subdir" / "deep.filtered.md").write_text("deep filtered")
    
    files = list(scan_files(tmp_path))
    filenames = [f.name for f in files]
    
    assert "normal.md" in filenames
    assert "other.md" in filenames
    assert "extra.filtered.md" not in filenames
    assert "deep.filtered.md" not in filenames

def test_metadata_processor_get_files_excludes_filtered(tmp_path):
    # Setup files
    (tmp_path / "doc.md").write_text("content")
    (tmp_path / "doc.filtered.md").write_text("filtered")
    
    mock_client = MagicMock()
    processor = MetadataProcessor(mock_client, tmp_path / "output")
    
    files = processor.get_files(tmp_path)
    filenames = [f.name for f in files]
    
    assert "doc.md" in filenames
    assert "doc.filtered.md" not in filenames
