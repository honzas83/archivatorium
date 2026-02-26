# Quickstart: Improved DOCX Export

This feature enhances the `ocrpolish` command-to-DOCX conversion by adding sophisticated header and footer management.

## Usage

Ensure your Markdown files use the `# Page N` marker to indicate page boundaries.

```bash
# Basic usage
ocrpolish --input data/raw --output data/processed --format docx --filter "CONFIDENTIAL|SECRET"
```

## Key Features

1.  **PDF Page Numbering**: Every page will have "PDF Page N" in the bottom-right footer.
2.  **Original Page Numbering**: If `-12-` appears on a page, it will be used in the header/footer metadata. If missing, the header/footer (except PDF Page N) will be cleared.
3.  **Metadata Migration**: Lines matching your `--filter` that appear near the `-X-` marker will be moved to the margins:
    - Above top `-X-`: Header Left
    - After top `-X-`: Header Right
    - Before bottom `-X-`: Footer Left
    - After bottom `-X-`: Footer Right

## Troubleshooting

- **Empty Pages**: If you have two `# Page` markers in a row, a blank page with the correct footer will be generated.
- **Marker Format**: Ensure the original page number follows the `-X-` format (e.g., `-1-`, `-15-`).
