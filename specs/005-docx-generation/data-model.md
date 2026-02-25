# Data Model: DOCX Generation

## Entities

### DocxConfiguration
Represents the settings for DOCX generation.
- **enabled**: boolean (Whether to generate DOCX)
- **font_name**: string (Default: "Consolas")
- **font_size**: integer (Default: 10)

### PageContent
Represents a single page of text extracted from the Markdown file.
- **page_number**: integer
- **content**: string (The raw text of the page)

## Relationships
- A **ProcessedFile** (from existing data model) can optionally produce one **DocxDocument**.
- A **DocxDocument** consists of one or more **PageContent** blocks.

## Validation Rules
- The output DOCX filename MUST match the input Markdown filename (with `.docx` extension).
- Every `# Page X` marker MUST trigger a new page in the DOCX.
