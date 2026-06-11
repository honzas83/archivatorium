# Implementation Plan: OCR Pipeline Integration

**Branch**: `030-ocr-pipeline` | **Date**: 2026-06-11 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/030-ocr-pipeline/spec.md`

## Summary

Integrate the existing Ollama OCR capabilities (`@ocr`) into the `ocrpolish` CLI as an `ocr` subcommand. This enables batch PDF to Markdown extraction while preserving the directory structure, with robust support for validating and resuming interrupted runs on a per-page basis.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: `click`, `ollama`, `PyPDF2`, `pdf2image`, `httpx`

**Storage**: Local Filesystem (input PDFs, output Markdown files)

**Testing**: `pytest`, `pytest-cov`

**Target Platform**: CLI (macOS, Linux)

**Project Type**: CLI Tool

**Performance Goals**: Maximize throughput for Ollama VLM processing; ensure fast page state validation.

**Constraints**: Resumable operations must minimize redundant VLM API calls (which are slow and expensive).

**Scale/Scope**: Processing directories containing hundreds of multipage PDFs.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **I. Quality-Driven Python Development**: Code will follow `ruff`, `flake8`, `mypy`, and include `pytest` coverage.
- [x] **II. CLI-First Interface**: Feature is exposed as `ocrpolish ocr`.
- [x] **III. Recursive Directory Processing**: Implemented via `pathlib.Path.rglob` to mirror structure.
- [x] **IV. Data Isolation**: Testing relies on the `data/` directory or temporary fixtures.
- [x] **V. Atomic Git Workflow**: Incremental commits will track the parser logic, CLI addition, and test updates separately.

## Project Structure

### Documentation (this feature)

```text
specs/030-ocr-pipeline/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    └── cli.md
```

### Source Code (repository root)

```text
src/
├── ocrpolish/
│   ├── cli.py             # Add the `ocr` subcommand
│   ├── ocr_engine.py      # Core OCR logic adapted from original ocr/ocr_multipage_tiff_ollama.py (now removed)
│   └── markdown_parser.py # Logic for parsing existing markdown to validate page state
tests/
├── test_ocr_engine.py
├── test_markdown_parser.py
└── test_cli.py
```

**Structure Decision**: The logic from the standalone script will be refactored into `ocr_engine.py` for API interaction and PDF manipulation. A new module `markdown_parser.py` will handle reading existing output files to determine the current progress state. The CLI command will be integrated natively into `cli.py`.

## Complexity Tracking

*(No unjustified violations to track)*
