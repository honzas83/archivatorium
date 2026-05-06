from ocrpolish.utils.metadata import (
    extract_last_page_header,
    flatten_metadata,
    format_hierarchical_tag,
    normalize_obsidian_tags,
    parse_frontmatter,
    prepend_frontmatter,
    stringify_frontmatter,
    safe_read_text,
    safe_identifier,
)


def test_safe_identifier() -> None:
    assert safe_identifier("NPG(SG)N(68)1") == "NPG-SG-N-68-1"
    assert safe_identifier("AC/137-D/498") == "AC-137-D-498"
    assert safe_identifier("Safe:Key_123-") == "Safe:Key_123"
    assert safe_identifier("Unsafe!@#$%^&*()") == "Unsafe"
    assert safe_identifier("") == "unknown"


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
    content = """# Page 1
Some content
# Page 2
More content
# Page 10
Last page"""
    assert extract_last_page_header(content) == 10

    assert extract_last_page_header("No page headers here") is None

    # Middle of line shouldn't match if it's not a header
    assert extract_last_page_header("Text # Page 5") is None


def test_parse_frontmatter_valid() -> None:
    content = "---\ntitle: Test\nauthor: John\n---\nBody content"
    metadata, body = parse_frontmatter(content)
    assert metadata == {"title": "Test", "author": "John"}
    assert body == "Body content"


def test_parse_frontmatter_no_frontmatter() -> None:
    content = "Just content"
    metadata, body = parse_frontmatter(content)
    assert metadata == {}
    assert body == "Just content"


def test_parse_frontmatter_malformed() -> None:
    content = "---\ntitle: Test\nBody content"  # Missing closing ---
    metadata, body = parse_frontmatter(content)
    assert metadata == {}
    assert body == content


def test_stringify_frontmatter() -> None:
    metadata = {"title": "Test", "author": "John"}
    yaml_str = stringify_frontmatter(metadata)
    assert "---\ntitle: Test\nauthor: John\n---\n" in yaml_str


def test_prepend_frontmatter() -> None:
    content = "Existing content"
    metadata = {"title": "New"}
    result = prepend_frontmatter(content, metadata)
    assert result.startswith("---\ntitle: New\n---\n")
    assert "Existing content" in result


def test_prepend_frontmatter_merge() -> None:
    content = "---\ntitle: Old\n---\nBody"
    metadata = {"author": "New"}
    result = prepend_frontmatter(content, metadata)
    assert "title: Old" in result
    assert "author: New" in result
    assert "Body" in result


def test_flatten_metadata() -> None:
    data = {"title": "Document", "correspondence": {"sender": "John", "details": {"date": "2024"}}}
    expected = {
        "title": "Document",
        "correspondence_sender": "John",
        "correspondence_details_date": "2024",
    }
    assert flatten_metadata(data) == expected


def test_normalize_obsidian_tags() -> None:
    tags = ["#NATO", " #Security ", "Deep State", "#Cold War", "1968", "2025"]
    expected = ["NATO", "Security", "DeepState", "ColdWar", "Year1968", "Year2025"]
    assert normalize_obsidian_tags(tags) == expected


def test_safe_read_text_with_invalid_utf8(tmp_path):
    # Create a file with invalid UTF-8 bytes
    # \xff is not a valid UTF-8 start byte
    file_path = tmp_path / "invalid.txt"
    with open(file_path, "wb") as f:
        f.write(b"Hello \xff World")
    
    # safe_read_text should not crash and should replace \xff with \ufffd
    content = safe_read_text(file_path)
    assert "Hello" in content
    assert "World" in content
    assert "\ufffd" in content


def test_safe_read_text_normal(tmp_path):
    file_path = tmp_path / "normal.txt"
    file_path.write_text("Standard content", encoding="utf-8")
    
    content = safe_read_text(file_path)
    assert content == "Standard content"
