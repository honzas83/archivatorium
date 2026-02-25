from pathlib import Path

from docx import Document
from docx.shared import Pt

from ocrpolish.utils.docx_utils import calculate_font_size, create_docx_from_pages, split_markdown_by_pages


def test_split_markdown_by_pages_removes_markers() -> None:
    content = "# Page 1\nContent 1\n---\n# Page 2\nContent 2\n---\nContent 3"
    pages = split_markdown_by_pages(content)
    assert len(pages) == 3
    for page in pages:
        assert "---" not in page
        assert "# Page" not in page
    assert pages[0] == "Content 1"
    assert pages[1] == "Content 2"
    assert pages[2] == "Content 3"


def test_split_markdown_by_pages_filters_empty() -> None:
    content = "Content 1\n---\n---\nContent 2"
    pages = split_markdown_by_pages(content)
    assert len(pages) == 2
    assert pages[0] == "Content 1"
    assert pages[1] == "Content 2"


def test_calculate_font_size() -> None:
    # Under limit
    text_short = "Line\n" * 10
    assert calculate_font_size(text_short, base_size=10, max_lines=50) == 10.0
    
    # Over limit
    text_long = "Line\n" * 100
    # 50 / 100 * 10 = 5.0, but capped at 6.0
    assert calculate_font_size(text_long, base_size=10, max_lines=50) == 6.0
    
    # Mid range
    text_mid = "Line\n" * 80
    # 50 / 80 * 10 = 6.25
    assert calculate_font_size(text_mid, base_size=10, max_lines=50) == 6.25


def test_create_docx_scaling(tmp_path: Path) -> None:
    # One short page (1 line), one very long page (100 lines)
    pages = ["Short page", "Long\n" * 100]
    output_path = tmp_path / "scale_test.docx"
    create_docx_from_pages(pages, output_path)

    doc = Document(str(output_path))
    # We expect 2 paragraphs now (one per page) because lines are grouped
    assert len(doc.paragraphs) == 2

    # First page should be 10pt (first paragraph)
    assert doc.paragraphs[0].runs[0].font.size == Pt(10)
    # Second page should be 6.5pt
    assert doc.paragraphs[1].runs[0].font.size == Pt(6.5)

def test_native_table_generation(tmp_path: Path) -> None:
    content = [
        "Header 1 | Header 2",
        "--- | ---",
        "Row 1 Col 1 | Row 1 Col 2"
    ]
    pages = ["\n".join(content)]
    output_path = tmp_path / "table_test.docx"
    create_docx_from_pages(pages, output_path)
    
    assert output_path.exists()
    doc = Document(str(output_path))
    
    # Verify a table was created
    assert len(doc.tables) == 1
    table = doc.tables[0]
    assert len(table.rows) == 2
    assert len(table.columns) == 2
    
    # Check content
    assert table.cell(0, 0).text == "Header 1"
    assert table.cell(1, 1).text == "Row 1 Col 2"
    
    # Check styling (Consolas)
    assert table.cell(0, 0).paragraphs[0].runs[0].font.name == "Consolas"
