# Data Model: DOCX Header/Footer Enhancement

## Entities

### PageMetadata
Represents the metadata extracted for a single logical page.
- `pdf_page_number`: Integer (extracted from `# Page N`)
- `original_page_number`: String (extracted from `-X-`, nullable)
- `header_left`: List[String] (Filtered lines before top `-X-`)
- `header_right`: List[String] (Filtered lines after top `-X-`)
- `footer_left`: List[String] (Filtered lines before bottom `-X-`)
- `footer_right`: List[String] (Filtered lines after bottom `-X-`)

### DocxSection
Mapping of a `PageMetadata` to a DOCX section.
- `section_index`: Integer
- `content`: List[String] (The body text for this page)

## Relationships
- A `Document` consists of multiple `PageMetadata` blocks.
- Each `PageMetadata` block corresponds to one `DocxSection`.

## Validation Rules
- `pdf_page_number` must be positive.
- If multiple filtered lines are in the same slot, they are joined with " | ".
- "PDF Page N" is always appended to `footer_right`.
