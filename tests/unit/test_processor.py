from pathlib import Path

from ocrpolish.data_model import ProcessingConfig
from ocrpolish.processor import clean_lines, is_page_number


def test_is_page_number() -> None:
    assert is_page_number("# Page 3") is True
    assert is_page_number("1-1") is True
    assert is_page_number("Page 42") is True
    assert is_page_number("5") is True
    assert is_page_number("Normal text") is False

def test_clean_lines_removes_headers() -> None:
    lines = [
        "HEADER\n",
        "Content line 1\n",
        "Content line 2\n",
        "FOOTER\n"
    ]
    global_headers = {"HEADER", "FOOTER"}
    config = ProcessingConfig(Path("in"), Path("out"), typewriter_width=80)
    
    result = clean_lines(lines, global_headers, config)
    # With NO merging, they stay as separate lines
    assert result == ["Content line 1", "Content line 2"]

def test_clean_lines_preserves_page_numbers() -> None:
    lines = [
        "HEADER\n",
        "Content\n",
        "# Page 1\n"
    ]
    global_headers = {"HEADER", "# Page 1"}
    config = ProcessingConfig(Path("in"), Path("out"), typewriter_width=80)
    
    result = clean_lines(lines, global_headers, config)
    assert "Content" in result
    assert "# Page 1" in result
    assert "HEADER" not in result

def test_line_wrapping_and_spacing() -> None:
    # Testing wrap-only, no merge
    long_line = (
        "This is a very long line that should be wrapped because it exceeds "
        "the typewriter width limit of forty characters."
    )
    lines = [
        long_line + "\n",
        "Short line.\n",
        "\n",
        "- List item\n"
    ]
    config = ProcessingConfig(Path("in"), Path("out"), typewriter_width=40)
    
    result = clean_lines(lines, set(), config)
    
    assert result[0] == "This is a very long line that should be"
    assert result[1] == "wrapped because it exceeds the"
    assert result[2] == "typewriter width limit of forty"
    assert result[3] == "characters."
    assert result[4] == "Short line."
    assert result[5] == ""
    assert result[6] == "- List item"

def test_no_merging_of_short_lines() -> None:
    lines = [
        "Line 1\n",
        "Line 2\n"
    ]
    config = ProcessingConfig(Path("in"), Path("out"), typewriter_width=80)
    result = clean_lines(lines, set(), config)
    assert result == ["Line 1", "Line 2"]
