# Quickstart: Validate Qwen 3.8 Markdown OCR Mode

## Prerequisites

- Project environment installed with the verified Ollama client version.
- Feature implementation complete on the Feature 038 branch.
- For automated validation, no live model or archival data is required.
- For behavioral review, an operator-accessible Qwen 3.8 model and disposable representative pages are required; those pages and outputs remain outside version control.

## 1. Validate the mode and request contracts

Run the focused OCR tests:

```bash
.venv/bin/python -m pytest -q tests/unit/test_ocr_engine.py tests/integration/test_ocr_cli.py
```

Expected outcome:

- `qwen38` is accepted by the existing mode option.
- Its exact system and user prompts match [contracts/qwen38-ocr-profile.md](contracts/qwen38-ocr-profile.md).
- Its request uses the exact selected model identifier, optional previous-page context, established general OCR options, non-streaming behavior, and `think="high"`.
- Retries reuse the identical request.
- Standard remains unchanged and omits the reasoning field; GLM remains `false`; FireRed continues to omit it.
- Inline reasoning cleanup, shared-indent cleanup, resume behavior, timing, and saved output regressions pass.

## 2. Inspect prompt requirements

Review the exact contract and confirm it contains all of these unambiguous rules:

- Output only pure Markdown transcription, without generated HTML.
- Mark supported heading hierarchy with `#`, `##`, `###`, and subsequent ATX levels; do not mark ordinary prose as headings.
- Put every prose paragraph on one physical line and separate distinct paragraphs with one blank line.
- Start top-level Markdown blocks at column one and avoid copied page-layout indentation.
- Use pipe tables when structure is clear and fenced plain text otherwise.
- Apply artificial character de-spacing anywhere in text, with the exact example `N A T O   S E C R E T` → `NATO SECRET`.
- Never infer or normalize typewritten characters into `{` or `}`; output a curly brace only when it is unambiguously visible.
- Preserve source content and avoid copying previous-page context that is absent from the current image.

## 3. Run a disposable Qwen 3.8 sample

Use the actual installed model identifier in place of the placeholder:

```bash
.venv/bin/python -m archivatorium.cli ocr \
  --mode qwen38 \
  --model '<qwen3.8-model>' \
  /path/to/disposable-input \
  /path/to/disposable-output
```

Use representative pages containing:

1. A title, section, subsection, ordinary prose, and a list.
2. A prose paragraph visually wrapped across several source lines followed by a distinct paragraph.
3. Artificially spaced text in multiple contexts: a heading, an ordinary sentence, a label, and a table cell.
4. A clear table and an ambiguous or fixed-width layout.
5. Literal HTML-like source text, unreadable text, and a blank page.
6. Ambiguous typewritten glyphs that might otherwise be normalized into curly braces, plus any genuinely visible brace available for a positive control.

Expected outcome:

- Titles and supported sublevels use correct and consistent ATX markers; prose is not promoted to a heading.
- Each prose paragraph is a single unwrapped line, while headings, list items, and table rows remain distinct blocks.
- Artificial spacing is removed wherever it occurs, and normal word boundaries remain. In particular, `N A T O   S E C R E T` becomes `NATO SECRET`.
- Ambiguous typewritten glyphs do not become `{` or `}`; a curly brace appears only when it is unambiguously visible in the source.
- Generated structure contains no HTML and no copied page-margin indentation.
- Tables use the required Markdown representation, source text remains faithful, and reasoning is absent.

## 4. Verify existing-mode isolation

Run mocked standard, GLM, and FireRed request tests and compare their exact request shapes with the pre-feature expectations.

Expected outcome: all three existing modes retain their prompts, previous-page behavior, reasoning fields, options, selected model handling, and retries. Only explicitly selected `qwen38` requests use the new contract and high reasoning.

## 5. Run project quality gates

```bash
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/python -m flake8 .
.venv/bin/python -m mypy .
.venv/bin/python -m pytest
.venv/bin/python -m coverage run -m pytest -o addopts=''
.venv/bin/python -m coverage report
```

Known unrelated working-tree files and local datasets are excluded from feature commits. Any pre-existing repository-wide quality finding must be reported separately from Feature 038 results.
