from ocrpolish.utils.metadata import (
    extract_last_page_header,
    format_bibtex_citation,
    format_hierarchical_tag,
    format_metadata_table,
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
    # New logic: count of headers, so 2
    assert extract_last_page_header(content) == 2
    assert extract_last_page_header("No pages here") is None


def test_format_bibtex_citation_date() -> None:
    data = {
        "archive_code": "NPG-D-73-10",
        "author_name": "E. F. Luff",
        "title": "Nuclear Planning Group",
        "date": "1973-10-05"
    }
    bibtex = format_bibtex_citation(data)
    assert "date = {1973-10-05}" in bibtex
    assert "@misc{NPG-D-73-10" in bibtex
    assert "author = {Luff, E. F.}" in bibtex


def test_format_metadata_table_icons() -> None:
    data = {
        "title": "Test Title",
        "pages": 10,
        "date": "2026-05-07",
        "references": ["Ref1", "Ref2"]
    }
    table = format_metadata_table(data)
    assert "≡&nbsp;**title**:" in table
    assert "№&nbsp;**pages**:" in table
    assert "🗓&nbsp;**date**:" in table
    assert "☰&nbsp;references:" in table
    assert "**Test Title**" in table
    assert "**10**" in table
    assert "**2026-05-07**" in table
    assert "Ref1<br>Ref2" in table
    assert "Ref1, Ref2" not in table
    assert "**Ref1<br>Ref2**" not in table
    assert "['Ref1', 'Ref2']" not in table
