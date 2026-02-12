# Research: Inverted Paragraph Merging & Wrapping

## Decisions

### Wrapping Algorithm
- **Decision**: Use `textwrap.wrap()` or `textwrap.TextWrapper` from the Python Standard Library.
- **Rationale**: `textwrap` is robust, well-tested, and handles word-wrapping without breaking words (unless necessary). It perfectly supports the requirement to wrap long lines while keeping subsequent lines flush left (by default).
- **Alternatives Considered**: Manual regex-based wrapping (rejected as complex and prone to errors).

### No-Merge Constraint
- **Decision**: The `merge_paragraphs` function in `processor.py` will be renamed to `wrap_lines` (or similar) and its loop will no longer accumulate lines into a buffer.
- **Rationale**: Direct alignment with user clarification: "Wrap Only (No Merging)".
- **Handling Leading Whitespace**: `textwrap.wrap()` can preserve or strip leading whitespace. Since the user chose "Flush Left" for wrapped lines, we will ensure that `subsequent_indent=""` is used (which is the default).

### Protection of Markdown
- **Decision**: Lines identified as "protected" (via `should_protect_line`) will bypass the wrapping logic entirely.
- **Rationale**: Ensures structural elements like `# Page 1` or lists are not corrupted by the character-count limit.
