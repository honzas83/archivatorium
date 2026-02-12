# Quickstart: Inverted Paragraph Merging & Wrapping

## New Behavior

The tool now focuses on **wrapping long lines** rather than merging short ones.

### Example

**Input**:
```text
This is a very very long line that exceeds the eighty character limit and should be wrapped into multiple shorter lines.
This is a short line.
It stays on its own line.
```

**Output (width=40)**:
```text
This is a very very long line that
exceeds the eighty character limit and
should be wrapped into multiple shorter
lines.
This is a short line.
It stays on its own line.
```

## Running with the new logic

```bash
python -m ocrpolish.cli data/raw/ data/wrapped/ --width 80
```

## Verification

Check that:
1. Long lines are broken at word boundaries.
2. Short lines preserve their original line breaks.
3. List items (`- item`) are NOT wrapped if they would break the list structure (protected).
