# Quickstart: OCR Pipeline Integration

This guide provides end-to-end validation scenarios for the OCR pipeline feature.

## Prerequisites

1. Ensure the `ocrpolish` CLI is installed and updated (`pip install -e .`).
2. An accessible Ollama server with the `qwen3.5:9b` or `qwen3-vl:4b` model downloaded.
3. Sample PDF files placed in `data/test_pdfs/`.
4. `poppler` must be installed on the system (e.g. `brew install poppler` on macOS or `apt-get install poppler-utils` on Ubuntu) for `pdf2image` to function.

## Scenario 1: Initial Processing

Run the OCR pipeline on a fresh directory.

```bash
mkdir -p data/test_pdfs/subdir
cp path/to/sample1.pdf data/test_pdfs/
cp path/to/sample2.pdf data/test_pdfs/subdir/

ocrpolish ocr data/test_pdfs data/ocr_output \
    --host "http://localhost:11434" \
    --model "qwen3-vl:4b" \
    --dpi 150
```

**Expected Outcome**:
- `data/ocr_output/sample1.md` is generated.
- `data/ocr_output/subdir/sample2.md` is generated.
- Both files contain the transcribed text with page headers (e.g., `---\n\n# Page 1\n\n`).

## Scenario 2: Resumption and Validation

Validate that the pipeline can resume processing if pages are missing.

1. Open `data/ocr_output/sample1.md` in an editor.
2. Delete the text content for "Page 2" (leaving the header or removing the block entirely).
3. Re-run the exact same command from Scenario 1.

**Expected Outcome**:
- The CLI logs indicate that it is skipping Page 1 and any other existing pages.
- The CLI logs indicate that it is extracting context (from Page 1) and re-running the VLM only for Page 2.
- `data/ocr_output/sample1.md` is updated with the freshly transcribed content for Page 2, in the correct sequential location.
