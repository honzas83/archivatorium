import pytest

from ocrpolish.utils.metadata import (
    format_bibtex_citation,
    format_chicago_citation,
    format_harvard_citation,
    generate_citation_callout,
)


@pytest.fixture
def sample_metadata() -> dict[str, str]:
    return {
        "author_name": "John Doe",
        "title": "NATO Defense Strategy 1968",
        "date": "1968-05-12",
        "author_institution": "NATO Headquarters",
        "archive_code": "NPG(SG)N(68)1",
        "url_date": "2026-05-06",
        # Default placeholder parameters
        "platform_name": "NATO Archive Obsidian",
        "url": "https://nato-obsidian.kky.zcu.cz/NPG-SG-N-68-1"
    }

def test_format_chicago_citation(sample_metadata: dict[str, str]) -> None:
    expected = "John, Doe, “NATO Defense Strategy 1968,” 1968/05/12, NATO Headquarters, NPG(SG)N(68)1, NATO Archive Obsidian, https://nato-obsidian.kky.zcu.cz/NPG-SG-N-68-1, 2026-05-06."  # noqa: E501
    result = format_chicago_citation(sample_metadata)
    assert result == expected

def test_format_harvard_citation(sample_metadata: dict[str, str]) -> None:
    expected = "Doe, J. (1968). “NATO Defense Strategy 1968,” NATO Headquarters, NPG(SG)N(68)1, NATO Archive Obsidian, https://nato-obsidian.kky.zcu.cz/NPG-SG-N-68-1, 2026-05-06."  # noqa: E501
    result = format_harvard_citation(sample_metadata)
    assert result == expected

def test_format_bibtex_citation(sample_metadata: dict[str, str]) -> None:
    expected = (
        "@misc{NPG-SG-N-68-1,\n"
        "  author = {Doe, John},\n"
        "  title = {NATO Defense Strategy 1968},\n"
        "  year = {1968},\n"
        "  month = {May},\n"
        "  day = {12},\n"
        "  note = {NATO Headquarters, NPG(SG)N(68)1, NATO Archive Obsidian},\n"
        "  url = {https://nato-obsidian.kky.zcu.cz/NPG-SG-N-68-1},\n"
        "  urldate = {2026-05-06}\n"
        "}"
    )
    result = format_bibtex_citation(sample_metadata)
    assert result == expected

def test_generate_citation_callout(sample_metadata: dict[str, str]) -> None:
    callout = generate_citation_callout(sample_metadata)
    assert "> [!citing this document]" in callout
    assert "> **Chicago**:" in callout
    assert "> **Harvard**:" in callout
    assert "> **BibTeX**:" in callout
    assert "John, Doe" in callout
    assert "Doe, J. (1968)" in callout
    assert "@misc{NPG-SG-N-68-1" in callout


def test_default_platform_and_url_placeholders() -> None:
    metadata = {
        "author_name": "Jane Smith",
        "title": "A Test Title",
        "date": "1970-10-25",
        "archive_code": "TEST-123",
        "url_date": "2026-05-06"
    }
    
    chicago = format_chicago_citation(metadata)
    assert "NATO Archive Obsidian" in chicago
    assert "https://nato-obsidian.kky.zcu.cz/TEST-123" in chicago

    bibtex = format_bibtex_citation(metadata)
    assert "NATO Archive Obsidian" in bibtex
    assert "https://nato-obsidian.kky.zcu.cz/TEST-123" in bibtex


def test_author_fallback_to_institution() -> None:
    metadata = {
        "author_name": "",
        "author_institution": "Nuclear Planning Group",
        "title": "Corrigendum to Document NPG/D(73)12",
        "date": "1975-10-24",
        "archive_code": "NPG/D(73)12-COR1",
        "url_date": "2026-05-06"
    }
    
    chicago = format_chicago_citation(metadata)
    # Should start with institution name
    assert chicago.startswith("Nuclear Planning Group, “Corrigendum to Document NPG/D(73)12,”")
    
    harvard = format_harvard_citation(metadata)
    assert harvard.startswith("Nuclear Planning Group (1975). “Corrigendum to Document NPG/D(73)12,”")
    
    bibtex = format_bibtex_citation(metadata)
    assert "author = {Nuclear Planning Group}" in bibtex
