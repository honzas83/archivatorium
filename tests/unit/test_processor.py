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
    config = ProcessingConfig(Path("in"), Path("out"))
    
    result = clean_lines(lines, global_headers, config)
    assert "Content line 1 Content line 2" in result
    assert "HEADER" not in result
    assert "FOOTER" not in result

def test_clean_lines_preserves_page_numbers() -> None:
    lines = [
        "HEADER\n",
        "Content\n",
        "# Page 1\n"
    ]
    global_headers = {"HEADER", "# Page 1"}
    config = ProcessingConfig(Path("in"), Path("out"))
    
    result = clean_lines(lines, global_headers, config)
    assert "Content" in result
    assert "# Page 1" in result
    assert "HEADER" not in result

def test_paragraph_merging_and_spacing() -> None:
    lines = [
        "This is a line\n",
        "that should be merged.\n",
        "\n",
        "This is a new paragraph.\n",
        "- This is a list item\n",
        "- Another list item\n"
    ]
    config = ProcessingConfig(Path("in"), Path("out"))
    
    result = clean_lines(lines, set(), config)
    
    assert "This is a line that should be merged." in result
    assert "" in result  # Blank line
    assert "This is a new paragraph." in result
    assert "- This is a list item" in result
    assert "- Another list item" in result
    
    # Verify exact line sequence
    # Note: clean_lines returns a list of lines without newlines
    # Expected: 
    # [
    #   "This is a line that should be merged.",
    #   "",
    #   "This is a new paragraph.",
    #   "- This is a list item",
    #   "- Another list item"
    # ]
    assert result == [
        "This is a line that should be merged.",
        "",
        "This is a new paragraph.",
        "- This is a list item",
        "- Another list item"
    ]
