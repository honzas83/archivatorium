from pathlib import Path

from ocrpolish.data_model import ProcessingConfig
from ocrpolish.processor import clean_lines


def test_paragraph_separation() -> None:
    config = ProcessingConfig(input_dir=Path("."), output_dir=Path("."), typewriter_width=80)
    lines = ["Line 1", "", "Line 2"]
    cleaned, dropped = clean_lines(lines, set(), config)
    assert cleaned == ["Line 1", "", "Line 2"]


def test_markup_separation() -> None:
    config = ProcessingConfig(input_dir=Path("."), output_dir=Path("."), typewriter_width=80)
    lines = ["<PAGE 1>", "Some text."]
    cleaned, dropped = clean_lines(lines, set(), config)

    # NEW RULE: short lines stay together. No automatic separation.
    assert cleaned == ["<PAGE 1>", "Some text."]
