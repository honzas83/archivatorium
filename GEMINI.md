# ocrpolish Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-02-12

## Active Technologies
- Python 3.12 + `argparse` (CLI), `pathlib` (filesystem), `typing` (type hints) (001-ocr-post-processing)
- Local filesystem (input/output mirroring) (001-ocr-post-processing)
- Python 3.12 + `textwrap` (Python Standard Library) (002-wrap-long-paragraphs)
- Filesystem (input/output mirroring) (002-wrap-long-paragraphs)
- Python 3.12 + click, textwrap, collections.Counter (003-enhanced-filtering-wrapping)
- Filesystem (input/output directories, sidecar `.filtered.md` files) (003-enhanced-filtering-wrapping)
- Python 3.12 + `click`, `textwrap`, `unicodedata` (stdlib), `collections.Counter` (stdlib) (004-rework-filtering-wrapping)
- Filesystem (input/output directories, `.freq.txt` sidecar files) (004-rework-filtering-wrapping)
- Python 3.12 + `click`, `textwrap`, `unicodedata` (stdlib), `collections.Counter` (stdlib), `re` (stdlib) (004-rework-filtering-wrapping)
- Filesystem (input/output directories, consolidated `frequency.txt`) (004-rework-filtering-wrapping)
- Python 3.12 + `python-docx` (New), `argparse`, `pathlib` (005-docx-generation)
- Filesystem (input/output directories) (005-docx-generation)
- Python 3.12 + `python-docx`, `re`, `collections.Counter` (006-docx-header-footer)
- Python 3.12 + `python-docx`, `click`, `re` (007-docx-header-footer-enhancement)
- Python 3.12 + `click`, `ollama` (Python library), `pydantic`, `pyyaml` (008-ollama-metadata-extraction)
- Filesystem (recursive input/output directory mirroring) (008-ollama-metadata-extraction)

- Python 3.12 + `click` (CLI), `pathlib` (filesystem), `typing` (type hints) (001-ocr-post-processing)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.12: Follow standard conventions

## Recent Changes
- 008-ollama-metadata-extraction: Added Python 3.12 + `click`, `ollama` (Python library), `pydantic`, `pyyaml`
- 007-docx-header-footer-enhancement: Added Python 3.12 + `python-docx`, `click`, `re`
- 006-docx-header-footer: Added Python 3.12 + `python-docx`, `re`, `collections.Counter`


<!-- MANUAL ADDITIONS START -->
- **Repository Integrity:** NEVER add large data files (PDFs, images, or large Markdown datasets) to the repository. Always ensure such directories are ignored via `.gitignore`.
<!-- MANUAL ADDITIONS END -->

<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan
at specs/012-llm-flat-topic-extraction/plan.md
<!-- SPECKIT END -->
