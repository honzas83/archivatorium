from pathlib import Path

from archivatorium.data_model import ProcessingConfig
from archivatorium.processor import clean_lines


def test_wrap_lists_not_tables() -> None:
    config = ProcessingConfig(input_dir=Path("."), output_dir=Path("."), typewriter_width=20)

    lines = [
        "- This is a very long list item that should be wrapped.",
        "| Table | Header |",
        "|-------|--------|",
        "| Cell  | Data   |",
    ]

    cleaned, dropped = clean_lines(lines, set(), config)

    # List item should be wrapped
    assert "- This is a very" in cleaned
    assert any("long list item" in line for line in cleaned)

    # Table should NOT be wrapped (each line is short enough anyway, but we check protection)
    # Actually let's make a long table line
    long_table = "| This is a very long table cell that should NOT be wrapped even if it is long |"
    lines_with_table = [long_table]
    cleaned_table, _ = clean_lines(lines_with_table, set(), config)
    assert cleaned_table == [long_table]
