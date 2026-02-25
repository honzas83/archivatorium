# Quickstart: DOCX Generation

## Prerequisites
- Install `python-docx`:
  ```bash
  pip install python-docx
  ```

## Usage
To process OCR files and generate DOCX mirroring the pages:
```bash
python -m ocrpolish.cli data/raw data/output --docx
```

## Verifying Results
1. Check the `data/output` directory for `.docx` files.
2. Open a DOCX file and verify:
   - Page breaks correspond to the `# Page X` markers in the Markdown.
   - The font is a fixed-width font like Consolas.
   - The number of pages matches the original document structure.
