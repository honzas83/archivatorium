# Research: Improve DOCX Header and Footer Export

## 1. python-docx Section Management

### Decision
Use `document.add_section()` for every `# Page N` marker encountered in the Markdown file.

### Rationale
In `python-docx`, headers and footers are properties of a `Section`. To have different headers/footers for different pages (or groups of pages), we must create new sections. By setting `section.header.is_linked_to_previous = False` and `section.footer.is_linked_to_previous = False`, we can isolate the metadata for each page as required by the spec.

### Alternatives Considered
- Using `document.add_page_break()`: This only moves content to the next page but doesn't allow independent header/footer management easily without complex field codes.
- Global headers/footers: Rejected because the spec requires page-specific metadata (PDF Page N and original page numbers).

---

## 2. Alignment within Headers and Footers

### Decision
Use tab stops in the header/footer paragraphs.

### Rationale
`python-docx` allows setting tab stops on paragraphs. A common pattern for headers is to have a left-aligned tab at the start and a right-aligned tab at the right margin. We can then insert text like `[Left Text]	[Right Text]` to achieve the desired alignment. For the footer, we can just use `paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT` if only right-aligned content exists, or tabs if we need both.

### Alternatives Considered
- Tables in headers/footers: Too complex for simple text alignment.
- Multiple paragraphs: Would create vertical space we might not want.

---

## 3. Metadata Proximity Detection

### Decision
Implement a "sliding window" or "look-ahead/look-behind" buffer during the Markdown parsing phase.

### Rationale
Since we need to identify filtered lines "near" `-X-` markers (within 5 lines), we can maintain a small buffer of lines. When an `-X-` marker is found, we check the previous 5 lines and the next 5 lines for matches against the filter.

### Alternatives Considered
- Two-pass parsing: First find all markers, then scan. (Rejected: more overhead).
- Regex-based global scan: Harder to track "nearness" across multiple markers on the same page.

---

## 4. Blank Page Generation

### Decision
When two `# Page N` markers are adjacent (or separated only by whitespace/filtered lines), explicitly add an empty paragraph to the section before adding the next section.

### Rationale
`python-docx` might not render a section if it has absolutely no content. Adding a single empty paragraph (or a non-breaking space) ensures the section exists and thus the header/footer are rendered.

### Alternatives Considered
- Just adding sections: Might result in merged pages if the word processor optimizes empty sections.
