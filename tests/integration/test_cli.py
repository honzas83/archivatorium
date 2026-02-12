from pathlib import Path

from ocrpolish.cli import parse_args
from ocrpolish.utils.files import ensure_directory_exists, get_output_path, scan_files


def test_directory_mirroring(tmp_path: Path) -> None:
    # Setup
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    
    (input_dir / "subdir1").mkdir(parents=True)
    (input_dir / "subdir2/nested").mkdir(parents=True)
    
    file1 = input_dir / "file1.md"
    file2 = input_dir / "subdir1/file2.md"
    file3 = input_dir / "subdir2/nested/file3.md"
    file4 = input_dir / "ignored.txt"
    
    for f in [file1, file2, file3, file4]:
        f.write_text("content")
        
    # Execution
    config = parse_args([str(input_dir), str(output_dir)])
    expected_md_files = 3
    files = list(scan_files(config.input_dir, config.input_mask))
    
    assert len(files) == expected_md_files
    assert file4 not in files
    
    for f in files:
        out_p = get_output_path(f, config.input_dir, config.output_dir)
        ensure_directory_exists(out_p)
        out_p.write_text("processed")
        
    # Verification
    assert (output_dir / "file1.md").exists()
    assert (output_dir / "subdir1/file2.md").exists()
    assert (output_dir / "subdir2/nested/file3.md").exists()
    assert not (output_dir / "ignored.txt").exists()
