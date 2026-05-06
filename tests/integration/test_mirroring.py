import os

from ocrpolish.utils.metadata import mirror_file


def test_mirror_file_hardlink(tmp_path):
    source_dir = tmp_path / "source"
    target_dir = tmp_path / "target"
    source_dir.mkdir()
    
    source_file = source_dir / "test.pdf"
    source_file.write_bytes(b"PDF CONTENT")
    
    target_file = target_dir / "test.pdf"
    
    mirror_file(source_file, target_file)
    
    assert target_file.exists()
    assert target_file.read_bytes() == b"PDF CONTENT"
    
    # Check if it's a hardlink (same inode)
    # Note: This might fail on some filesystems (like shared drives in Docker), 
    # but on local Mac/Linux it should work.
    source_stat = os.stat(source_file)
    target_stat = os.stat(target_file)
    
    assert source_stat.st_ino == target_stat.st_ino

def test_mirror_file_fallback_on_exists(tmp_path):
    source_file = tmp_path / "source.txt"
    source_file.write_text("New Content")
    
    target_file = tmp_path / "target.txt"
    target_file.write_text("Old Content")
    
    # mirror_file should overwrite with copy if link fails or target exists
    mirror_file(source_file, target_file)
    
    assert target_file.read_text() == "New Content"
