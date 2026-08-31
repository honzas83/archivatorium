# Quickstart: Validate Qwen 3.8 OCR Output Normalization

## Prerequisites

- Python 3.12 project environment with dependencies installed.
- Poppler available for PDF rendering.
- For manual validation, an accessible OCR host with Qwen 3.8 available under the model identifier supplied to `--model`.
- Disposable input and output directories; do not use archival originals for validation.

Automated validation mocks model responses and timing and requires no model download or live credentials.

## 1. Run focused automated validation

```bash
.venv/bin/python -m pytest tests/unit/test_ocr_engine.py tests/integration/test_ocr_cli.py
```

Expected outcome: tests cover final-marker selection, no-marker behavior, leading blank separators, four/eight-space dedenting, unindented and tab-indented content, blank lines, direct page calls, saved Markdown, retries, resume skips, failures, zero-page timing, and stable timing-log fields.

## 2. Run Qwen 3.8 against a disposable PDF directory

```bash
.venv/bin/archivatorium ocr \
  --model qwen3.8 \
  /path/to/disposable-input \
  /path/to/disposable-output
```

Expected outcome: generated Markdown excludes every response prefix through the final `</think>` marker. Artificial indentation shared by every nonblank line is removed, while nested indentation remains. The selected model name and all existing standard-mode request behavior remain unchanged.

## 3. Inspect a mixed-indentation example

Use a mocked or controlled response containing:

```text
reasoning text</think>

    First line
        Nested line
    Final line
```

Expected saved page text:

```text
First line
    Nested line
Final line
```

See [contracts/ocr-output.md](contracts/ocr-output.md) for exact normalization order and tab behavior.

## 4. Verify timing output

Run OCR normally and inspect INFO output for one summary per processed PDF:

```text
OCR timing: attempted_pages=10 total_seconds=50.000 average_seconds_per_page=5.000
```

Resume a fully recognized PDF and run the same command again. Expected outcome: the summary reports `attempted_pages=0` and `average_seconds_per_page=unavailable`. A mocked retry or failed page remains one attempted page while its retry wait and failure time remain included.

## 5. Validate compatibility

Run the current standard, GLM, and FireRed modes with mocked model output that has neither a reasoning marker nor shared indentation.

Expected outcome: request shapes, model selection, page ordering, headers, filenames, retry behavior, and resumed-page skipping remain unchanged. Only the timing summary is newly visible.

## 6. Run project quality gates

```bash
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/flake8 .
.venv/bin/python -m mypy .
.venv/bin/python -m pytest
.venv/bin/coverage run -m pytest
.venv/bin/coverage report
```

Expected outcome: every constitutional quality gate passes before implementation is considered complete.
