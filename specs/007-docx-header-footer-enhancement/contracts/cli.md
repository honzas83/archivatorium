# CLI Contract: DOCX Header/Footer Enhancement

## Overview
The CLI interface remains largely unchanged, but the `--filter` argument now has a direct impact on the DOCX layout.

## Arguments

### `--filter` (or `-f`)
- **Type**: String (Regex pattern)
- **Role**: Identifies lines to be removed from the main body.
- **New Behavior**: Lines matching this pattern that are adjacent to `-X-` markers will be moved to the DOCX headers or footers instead of being simply discarded.

## Expectations
- The `--format docx` flag must be active for the header/footer logic to trigger.
- If `--filter` is not provided, no metadata migration will occur, but the "PDF Page N" and `-X-` logic will still apply based on the Markdown content.
