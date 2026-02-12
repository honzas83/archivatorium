from pathlib import Path

from ocrpolish.core import run_processing
from ocrpolish.data_model import ProcessingConfig


def test_full_cleaning_integration(tmp_path: Path) -> None:
    # Setup
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()
    
    # Create multiple files with identical header/footer
    header = "PUBLICLY DISCLOSED - NATO UNCLASSIFIED"
    footer = "NATO UNCLASSIFIED"
    
    # Long line to test wrapping
    long_body = (
        "This is a very long line that should be wrapped because it exceeds "
        "the typewriter width limit."
    )
    
    file1_content = (
        f"{header}\n\nContent of file 1\nwith multiple lines.\n\n" f"{long_body}\n\n{footer}"
    )
    file2_content = f"{header}\n\nContent of file 2\non a single line.\n\n{footer}"
    
    (input_dir / "doc1.md").write_text(file1_content)
    (input_dir / "doc2.md").write_text(file2_content)
    
    # Use a small width to trigger wrapping in the test
    config = ProcessingConfig(
        input_dir=input_dir,
        output_dir=output_dir,
        threshold=0.5,
        typewriter_width=40
    )
    
    # Execution
    run_processing(config)
    
    # Verification
    out1 = output_dir / "doc1.md"
    assert out1.exists()
    
    content1 = out1.read_text()
    
    # Headers/Footers should be gone
    assert header not in content1
    assert footer not in content1
    
    # Paragraphs should NOT be merged anymore (per new requirement)
    assert "Content of file 1\nwith multiple lines." in content1
    
    # Long body should be wrapped
    expected_wrap = (
        "This is a very long line that should be\n"
        "wrapped because it exceeds the\n"
        "typewriter width limit."
    )
    assert expected_wrap in content1
