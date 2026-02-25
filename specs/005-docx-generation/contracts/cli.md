# CLI Contract: DOCX Generation

## New Command Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--docx` | flag | `False` | Enable generation of DOCX files from processed Markdown. |

## Behavior Changes
- When `--docx` is provided, for every processed Markdown file, a corresponding `.docx` file will be created in the output directory.
- The DOCX file will preserve page boundaries defined by `---` and `# Page X` markers.
- The font will be set to a non-Courier fixed-width font (e.g., Consolas).
