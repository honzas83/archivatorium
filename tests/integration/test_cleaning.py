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
    
    file1_content = f"{header}\n\nContent of file 1\nwith multiple lines.\n\n{footer}"
    file2_content = f"{header}\n\nContent of file 2\non a single line.\n\n{footer}"
    
    (input_dir / "doc1.md").write_text(file1_content)
    (input_dir / "doc2.md").write_text(file2_content)
    
    config = ProcessingConfig(
        input_dir=input_dir,
        output_dir=output_dir,
        threshold=0.5
    )
    
    # Execution
    run_processing(config)
    
    # Verification
    out1 = output_dir / "doc1.md"
    out2 = output_dir / "doc2.md"
    
    assert out1.exists()
    assert out2.exists()
    
    content1 = out1.read_text()
    content2 = out2.read_text()
    
    # Headers/Footers should be gone
    assert header not in content1
    assert footer not in content1
    
    # Paragraphs should be merged
    assert "Content of file 1 with multiple lines." in content1
    assert "Content of file 2 on a single line." in content2
