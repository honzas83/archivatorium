# Quickstart: Validate FireRed OCR Mode

## Prerequisites

- Python 3.12 project environment with dependencies installed.
- Poppler available for PDF rendering.
- For manual validation, an accessible OCR host with the FireRed model selected by `--model`.
- A disposable input directory containing PDFs and a separate output directory.

Automated validation mocks the remote service and requires no model download or live credentials.

## 1. Run focused automated validation

```bash
.venv/bin/pytest tests/unit/test_ocr_engine.py tests/integration/test_ocr_cli.py
```

Expected outcome: tests verify the exact FireRed prompt, absence of a system prompt and neighboring-page text, retry and resume isolation, CLI selection, independent model selection, invalid mode rejection, and unchanged standard and GLM behavior.

## 2. Check the CLI contract

```bash
.venv/bin/archivatorium ocr --help
```

Expected outcome: help lists `--mode [standard|glm|firered]` with `standard` as the default, retains both directory arguments and existing inference options, and continues to expose `--model` independently. See [contracts/cli.md](contracts/cli.md).

## 3. Run FireRed mode against the configured host

```bash
.venv/bin/archivatorium ocr \
  --host http://ollama.example:11434 \
  --mode firered \
  --model firered-ocr \
  /path/to/input-pdfs \
  /path/to/firered-output
```

Expected outcome: each missing page produces normal Markdown output in page order. Each recognition uses the exact FireRed prompt and no recognized text from another page. Existing non-empty pages remain skipped during resume. See [data-model.md](data-model.md) for the request invariants.

## 4. Validate multipage resume isolation

1. Process a multipage PDF in FireRed mode.
2. Remove the content of a later page from the generated Markdown while leaving a recognizable preceding page.
3. Run the same command again and inspect the mocked request in automated coverage, or host-side request logs in a controlled environment.

Expected outcome: only the missing page is recognized, and its request has the FireRed prompt but no transcription from the prior page.

## 5. Validate compatibility

```bash
.venv/bin/archivatorium ocr --mode standard /path/to/input-pdfs /path/to/standard-output
.venv/bin/archivatorium ocr --mode glm --model glm-ocr /path/to/input-pdfs /path/to/glm-output
```

Expected outcome: standard requests preserve their system prompt and previous-page context; GLM requests preserve their existing native prompt and page isolation.

## 6. Run project quality gates

```bash
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/flake8 .
.venv/bin/mypy .
.venv/bin/pytest
.venv/bin/coverage run -m pytest
.venv/bin/coverage report
```

Expected outcome: all constitutional quality gates pass before the feature is complete.
