from ocrpolish.utils.metadata import (
    extract_last_page_header,
    format_hierarchical_tag,
)


def test_format_hierarchical_tag() -> None:
    # Single level (category + topic as originally envisioned)
    assert format_hierarchical_tag("State", "UK") == "#State/UK"
    # Multiple levels
    assert format_hierarchical_tag("City", "UK", "London") == "#City/UK/London"
    # Spaces replaced with hyphens
    assert format_hierarchical_tag("State", "United Kingdom") == "#State/United-Kingdom"
    # Handling empty topics
    assert format_hierarchical_tag("Org", "NATO", "") == "#Org/NATO"


def test_extract_last_page_header() -> None:
    content = "# Page 1\nSome text\n# Page 5\nMore text"
    assert extract_last_page_header(content) == 5
    assert extract_last_page_header("No pages here") is None
