# Data Model: OCR Pipeline Integration

## Core Entities

### OCRDocumentState

Tracks the processing state of a single PDF document based on its corresponding output markdown file.

**Fields**:
- `filepath: Path` - The absolute path to the input PDF.
- `total_pages: int` - Total number of pages in the PDF.
- `pages: Dict[int, str]` - A mapping of 1-based page numbers to their transcribed text content.
- `missing_pages: List[int]` - A derived list of pages that have not been recognized (either missing from the map or containing only whitespace).

**Validation Rules**:
- Page numbers must be between `1` and `total_pages`.

### OCRTaskConfig

Configuration for the Ollama connection and rendering settings.

**Fields**:
- `host: str` - The URL to the Ollama server.
- `user: Optional[str]` - DigestAuth username.
- `password: Optional[str]` - DigestAuth password.
- `model: str` - The VLM model name (e.g., `qwen3.5:9b`).
- `dpi: int` - Dots per inch for PDF-to-PNG rendering.

## State Transitions

- **Unprocessed** -> **Partial**: The OCR engine processes the first `k` pages before being interrupted.
- **Partial** -> **Complete**: The pipeline detects `missing_pages`, extracts contexts, processes the missing subset, and saves the fully merged document.
- **Complete** -> **Complete**: The validation parser detects `total_pages == len(pages)` with non-empty content, yielding a no-op skip.
