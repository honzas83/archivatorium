from ocrpolish.processor import wrap_lines, ProcessingConfig
from pathlib import Path

def test_table_without_leading_pipe():
    config = ProcessingConfig(input_dir=Path("."), output_dir=Path("."))
    lines = [
        "Header 1 | Header 2 | Header 3",
        "--- | --- | ---",
        "Row 1 Col 1 | Row 1 Col 2 | Row 1 Col 3"
    ]
    
    blocks = wrap_lines(lines, config)
    # If correctly detected as a table, it should be one block with 3 lines
    # and all lines should be aligned/padded.
    assert len(blocks) == 1
    formatted_lines = blocks[0][0]
    assert len(formatted_lines) == 3
    assert formatted_lines[0].startswith("|")
    assert formatted_lines[0].endswith("|")
    # Check alignment (roughly)
    assert "|" in formatted_lines[0]
