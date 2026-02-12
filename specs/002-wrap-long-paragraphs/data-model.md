# Data Model: Inverted Paragraph Merging & Wrapping

## Entities

### WrappingConfig (Updated ProcessingConfig)
- **Description**: Configuration for the wrapping pass.
- **Attributes**:
  - `typewriter_width`: int (Max characters per line).
  - `protected_prefixes`: list[str] (Lines starting with these skip wrapping).
  - `wrap_strategy`: string ("wrap-only").

## Logic Transitions

1. **Line Processing Loop**:
   - For each line in `filtered_lines`:
     - If line is `protected` or `empty`:
       - Append to `output` as-is.
     - Else if `len(line) > typewriter_width`:
       - Run `textwrap.wrap(line, width=typewriter_width)`.
       - Append all resulting wrapped lines to `output`.
     - Else:
       - Append to `output` as-is (preserves existing line breaks).

2. **Final Cleanup**:
   - Ensure exactly one blank line between paragraphs (where "paragraph" is now defined by the original document's blank lines).
