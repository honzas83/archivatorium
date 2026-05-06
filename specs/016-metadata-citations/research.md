# Research: Metadata Citations

## Existing Architecture Analysis

The `MetadataProcessor` in `ocrpolish/processor_metadata.py` is responsible for generating Obsidian Markdown files. It already handles:
- Frontmatter generation.
- Abstract and metadata callouts at the beginning of the file.
- Relative links to source PDFs.

The utilities in `ocrpolish/utils/metadata.py` provide `format_as_callout` which can be reused for the citation block.

## Design Decisions

### 1. Citation Formatting Logic
- **Decision**: Implement a dedicated utility or method to format the three citation styles (Chicago, Harvard, BibTeX).
- **Rationale**: Keeps `process_file` clean and allows for easier testing of citation formatting independently.

### 2. Name Parsing
- **Decision**: Expect `author_name` metadata field. If it contains multiple words, assume the last word is the surname and previous words are first names.
- **Rationale**: Simple heuristic that covers most cases in the current dataset. For more complex cases, future refinement may be needed.

### 3. Date Handling
- **Decision**: Parse the `YYYY-MM-DD` date field. If only `YYYY` is available, use `YYYY/01/01` for Chicago and `n.d.` (no date) where appropriate, or just the Year.
- **Rationale**: Ensures the templates are filled even with partial data.

### 4. BibTeX Citekey
- **Decision**: Use `ArchiveCode` as the `citekey` (e.g., `NPG-SG-N-68-1`).
- **Rationale**: User-specified preference (Option B).

### 5. URL Placeholder
- **Decision**: Use `https://nato-obsidian.kky.zcu.cz/[ArchiveCode]` as the default URL.
- **Rationale**: User-specified preference (Option B).

### 6. Integration Point
- **Decision**: Append the citation callout at the very end of the document in `MetadataProcessor.process_file`.
- **Rationale**: Consistent with the user request to "Place them at the end of the files".

## Alternatives Considered
- **Adding to Frontmatter**: Rejected as the user explicitly asked for an Obsidian callout at the end of the file.
- **Using a separate script**: Rejected as it's more efficient to do it during the initial file generation.
