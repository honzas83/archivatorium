# Research: DOCX Generation with Page Mirroring

## Decision: Use `python-docx` for DOCX generation
- **Rationale**: `python-docx` is the most mature and widely used library for creating and updating Microsoft Word (.docx) files in Python. It provides high-level abstractions for paragraphs, styles, and page breaks.
- **Alternatives considered**: 
  - `pypandoc`: Requires Pandoc installed on the system, which adds a heavy external dependency.
  - `mammoth`: Primarily focused on converting DOCX to HTML/Markdown, not the other way around.

## Decision: Implementation of Page Mirroring
- **Rationale**: The Markdown file uses `---` and `# Page X` markers. The processor will split the content by these markers. For each section, a new page will be started in the DOCX document using `document.add_page_break()` (except for the first page).
- **Alternatives considered**: Manually calculating line heights to fit a page, but this is extremely brittle and doesn't guarantee the "same number of pages" as requested by the user's specific markers.

## Decision: Font Selection
- **Rationale**: The requirement is "fixed-width font other than Courier New". We will use **"Consolas"** as the primary choice (common on Windows) with fallbacks like **"Roboto Mono"** or **"Courier"** (not Courier New) if necessary, or simply set the style to "Consolas" as it's a standard Microsoft Word font.
- **Alternatives considered**: Courier New (explicitly forbidden).

## Decision: Integration into `processor.py`
- **Rationale**: The existing `Processor` class handles the file iteration and cleaning. A new `DocxGenerator` utility or method within the processor will be called if the `--docx` flag is set.
- **Alternatives considered**: A separate standalone script, but integration into the main pipeline is more consistent with the project's architecture.
