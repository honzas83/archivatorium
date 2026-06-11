from ocrpolish.markdown_parser import MarkdownPageParser


def test_parse_pages_basic():
    content = """---

# Page 1

Content of page 1.

---

# Page 2

Content of page 2.
Line 2 of page 2."""

    pages = MarkdownPageParser.parse_pages(content)
    assert len(pages) == 2
    assert pages[1] == "Content of page 1."
    assert pages[2] == "Content of page 2.\nLine 2 of page 2."


def test_parse_pages_empty():
    pages = MarkdownPageParser.parse_pages("")
    assert len(pages) == 0


def test_parse_pages_no_markers():
    content = "Just some text without page headers."
    pages = MarkdownPageParser.parse_pages(content)
    assert len(pages) == 0


def test_parse_pages_missing_pages():
    content = """---

# Page 1

Content of page 1.

---

# Page 3

Content of page 3."""

    pages = MarkdownPageParser.parse_pages(content)
    assert len(pages) == 2
    assert 1 in pages
    assert 3 in pages
    assert 2 not in pages
