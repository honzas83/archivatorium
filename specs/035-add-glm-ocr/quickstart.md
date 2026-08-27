# Quickstart: Validate GLM OCR Mode

## Prerequisites

- Python 3.12 project environment with the repository dependencies installed.
- Poppler available for PDF rendering.
- For manual validation, access to an Ollama 0.9.0-or-newer API host containing the model selected with `--model`.
- A disposable input directory containing one or more PDFs and a separate output directory.

The automated tests mock the API and do not require a running Ollama server or downloaded model.

## 1. Run focused automated validation

```bash
.venv/bin/pytest tests/unit/test_ocr_engine.py tests/integration/test_ocr_cli.py
```

Expected outcome: tests verify the exact GLM request, all six defaults and overrides, model independence, no-context behavior for multipage/resume/retry flows, invalid-input rejection, and unchanged standard behavior.

## 2. Check the CLI contract

```bash
.venv/bin/archivatorium ocr --help
```

Expected outcome: help lists `--mode [standard|glm]` with default `standard` and the six inference override options, including `--repeat-last-n`, while retaining `INPUT_DIR OUTPUT_DIR`, the existing `--model` default, and all prior OCR options. See [contracts/cli.md](contracts/cli.md) for the complete contract.

## 3. Run GLM mode against the configured API host

```bash
.venv/bin/archivatorium ocr \
  --host http://ollama.example:11434 \
  --mode glm \
  --model glm-ocr \
  /path/to/input-pdfs \
  /path/to/glm-output
```

Expected outcome: each missing page produces Markdown output using independent GLM recognition. The API receives the native prompt, disabled thinking, and defaults described in [data-model.md](data-model.md). Existing non-empty pages are skipped during resume.

## 4. Validate explicit overrides

```bash
.venv/bin/archivatorium ocr \
  --host http://ollama.example:11434 \
  --mode glm \
  --model glm-ocr \
  --temperature 0.0 \
  --top-p 0.1 \
  --top-k 2 \
  --repeat-penalty 1.2 \
  --repeat-last-n 1024 \
  --num-predict 4096 \
  /path/to/input-pdfs \
  /path/to/glm-overridden-output
```

Expected outcome: explicit values replace only their corresponding GLM defaults. `temperature=0.0` is retained as a real override, and GLM prompting, disabled thinking, and page isolation remain active.

## 5. Validate backward compatibility

```bash
.venv/bin/archivatorium ocr \
  --host http://ollama.example:11434 \
  --mode standard \
  --model qwen3.5:9b \
  /path/to/input-pdfs \
  /path/to/standard-output
```

Expected outcome: explicit `--mode standard` and an omitted mode both retain the existing standard VLM prompts, prior-page context, inference values, resume behavior, and Markdown output structure.

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

Expected outcome: all constitutional quality gates pass before implementation is considered complete.

## Validation Record (2026-08-27)

- Focused OCR validation: `43 passed`; GLM request, `repeat_last_n=512` default and overrides, standard regression, model independence, resume, retry, and CLI rejection scenarios all passed.
- Full project validation: `284 passed, 1 skipped`; source-package coverage was 89%, including 93% for `archivatorium/ocr_engine.py` and 94% for `archivatorium/cli.py`.
- `ruff check .`: passed.
- `mypy .`: passed for 94 source files.
- Feature-file `ruff format --check` and `flake8`: passed.
- Full `ruff format --check .`: reports four pre-existing managed files under `.specify/scripts/python/`; they are outside this feature and were not reformatted.
- Full `flake8 .`: reports the pre-existing cognitive-complexity finding in `archivatorium/services/interlinking_service.py`; the GLM OCR files are clean.
- `coverage run -m pytest --no-cov` followed by `coverage report`: passed and produced a report. `--no-cov` prevents the project's auto-enabled pytest-cov plugin from consuming the outer coverage session.
- `archivatorium ocr --help`: verified `--mode [standard|glm]`, default `standard`, both positional directories, independent `--model`, and all six inference options.
- Live remote-API examples were not executed because they require user-provided PDFs, output paths, credentials, and an Ollama 0.9.0+ host. Their request contract is covered by mocked integration tests.
