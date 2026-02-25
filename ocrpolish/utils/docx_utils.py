import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_BREAK
from docx.shared import Pt


def split_markdown_by_pages(content: str) -> list[str]:
    """
    Split markdown content into pages based on '---' and '# Page X' markers.
    Ensures markers themselves are removed from the output content.
    """
    # Normalize line endings and split by lines to handle markers accurately
    lines = content.splitlines()
    pages: list[str] = []
    current_page: list[str] = []

    for line in lines:
        trimmed = line.strip()
        # Detect page boundaries: '---' or '# Page X'
        if trimmed == "---" or re.match(r"^#\s*Page\s+\d+$", trimmed, re.IGNORECASE):
            if current_page:
                pages.append("\n".join(current_page).strip())
                current_page = []
            continue
        
        current_page.append(line)

    if current_page:
        pages.append("\n".join(current_page).strip())

    # Filter out empty pages to avoid unwanted artifacts
    return [p for p in pages if p.strip()]


def calculate_font_size(text: str, base_size: int = 10, max_lines: int = 50) -> float:
    """
    Heuristic to scale font size so that content fits on a single DOCX page.
    Assumes standard A4/Letter margins.
    """
    lines = text.splitlines()
    line_count = len(lines)
    
    if line_count <= max_lines:
        return float(base_size)
    
    # Scale down proportionally if we exceed the target line count
    scale_factor = max_lines / line_count
    # Don't scale below 6pt for readability
    return max(6.0, base_size * scale_factor)


def create_docx_from_pages(
    pages: list[str],
    output_path: Path,
    font_name: str = "Consolas",
    font_size: int = 10,
) -> None:
    """
    Create a DOCX file with optimized performance and tight line spacing.
    """
    doc = Document()
    
    # Adjust margins slightly to maximize space (0.5 inch margins)
    for section in doc.sections:
        section.top_margin = section.bottom_margin = Pt(36)
        section.left_margin = section.right_margin = Pt(36)

    for i, page_content in enumerate(pages):
        dynamic_size = calculate_font_size(page_content, base_size=font_size, max_lines=65)

        # Process lines to detect and render tables vs text
        lines = page_content.splitlines()
        line_idx = 0
        first_element_on_page = True
        
        while line_idx < len(lines):
            line = lines[line_idx]
            
            # Simple table detection
            is_table = line.strip().startswith("|")
            if not is_table and line_idx + 1 < len(lines):
                next_line = lines[line_idx + 1].strip()
                if "|" in line and "-" in next_line and ("|" in next_line or "---" in next_line):
                    is_table = True

            if is_table:
                table_lines = []
                while line_idx < len(lines) and "|" in lines[line_idx]:
                    table_lines.append(lines[line_idx])
                    line_idx += 1
                
                # Handle page break before table
                if i > 0 and first_element_on_page:
                    p_break = doc.add_paragraph()
                    p_break.paragraph_format.line_spacing = 1.0
                    p_break.paragraph_format.space_after = Pt(0)
                    p_break.add_run().add_break(WD_BREAK.PAGE)
                
                if table_lines:
                    _render_table(doc, table_lines, font_name, dynamic_size)
                first_element_on_page = False
            else:
                # Group consecutive plain text lines into ONE paragraph for performance
                text_block = []
                while line_idx < len(lines):
                    curr = lines[line_idx]
                    # Stop if we hit a table
                    curr_is_table = curr.strip().startswith("|")
                    if not curr_is_table and line_idx + 1 < len(lines):
                        next_curr = lines[line_idx + 1].strip()
                        if "|" in curr and "-" in next_curr and ("|" in next_curr or "---" in next_curr):
                            curr_is_table = True
                    
                    if curr_is_table:
                        break
                    
                    text_block.append(curr)
                    line_idx += 1
                
                if text_block:
                    p = doc.add_paragraph()
                    # Set tight spacing
                    pf = p.paragraph_format
                    pf.line_spacing = 1.0
                    pf.space_before = Pt(0)
                    pf.space_after = Pt(0)
                    
                    run = p.add_run()
                    # Add page break if this is the first block on a non-first page
                    if i > 0 and first_element_on_page:
                        run.add_break(WD_BREAK.PAGE)
                    
                    # Use explicit line breaks for each line in the block
                    for j, text_line in enumerate(text_block):
                        run.add_text(text_line)
                        if j < len(text_block) - 1:
                            run.add_break()
                            
                    run.font.name = font_name
                    run.font.size = Pt(dynamic_size)
                first_element_on_page = False

    doc.save(str(output_path))


def _render_table(doc: Document, table_lines: list[str], font_name: str, font_size: float) -> None:
    """Helper to convert markdown table lines into a native Word table."""
    # Parse rows and skip separator lines
    rows_data = []
    for line in table_lines:
        stripped = line.strip()
        if not stripped:
            continue
            
        # Check if it's a separator line: only contains | - : and whitespace, and has at least one -
        is_sep = False
        if "-" in stripped:
            # Remove all valid separator characters
            remaining = stripped.replace("|", "").replace("-", "").replace(":", "").replace(" ", "")
            if len(remaining) == 0:
                is_sep = True
        
        if is_sep:
            continue
            
        # Parse content
        content = stripped
        if content.startswith("|"): content = content[1:]
        if content.endswith("|"): content = content[:-1]
            
        cells = [c.strip() for c in content.split("|")]
        rows_data.append(cells)

    if not rows_data:
        return

    num_cols = max(len(r) for r in rows_data)
    table = doc.add_table(rows=len(rows_data), cols=num_cols)
    table.style = "Table Grid"
    table.autofit = True

    for r_idx, row_data in enumerate(rows_data):
        row = table.rows[r_idx]
        row_cells = row.cells
        for c_idx, cell_value in enumerate(row_data):
            if c_idx < num_cols:
                cell = row_cells[c_idx]
                cell.text = cell_value
                # Apply font styling to the paragraph in the cell
                for paragraph in cell.paragraphs:
                    # Set tight spacing for table cells
                    pf = paragraph.paragraph_format
                    pf.line_spacing = 1.0
                    pf.space_before = Pt(0)
                    pf.space_after = Pt(0)
                    for run in paragraph.runs:
                        run.font.name = font_name
                        run.font.size = Pt(font_size)
