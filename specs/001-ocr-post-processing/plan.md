# Implementation Plan: OCR Post-Processing

**Branch**: `001-ocr-post-processing` | **Date**: 2026-02-12 | **Spec**: /specs/001-ocr-post-processing/spec.md
**Input**: Feature specification from `/specs/001-ocr-post-processing/spec.md`

## Summary

Implement a Python CLI tool, `ocrpolish`, to clean LLM-OCR output by removing statistical headers/footers and reformatting broken paragraphs while preserving directory structures. The tool will use a two-pass streaming approach to handle large datasets efficiently.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: `argparse` (CLI), `pathlib` (filesystem), `typing` (type hints)
**Storage**: Local filesystem (input/output mirroring)
**Testing**: `pytest`, `coverage`
**Target Platform**: CLI
**Project Type**: Single project
**Performance Goals**: Support processing of 1000+ files with 2-pass streaming to maintain low memory footprint.
**Constraints**: Recursive processing, statistical header detection (50%+ threshold), markdown element protection.
**Scale/Scope**: Initial version focuses on line-based statistical cleaning and paragraph merging via a simple CLI interface.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **I. Quality-Driven Python Development**: Python 3.12, ruff, flake8, mypy, pytest confirmed.
- [x] **II. CLI-First Interface**: `argparse` chosen for standard POSIX-style CLI as per user preference.
- [x] **III. Recursive Directory Processing**: `pathlib` will be used for recursive scanning and mirroring.
- [x] **IV. Data Isolation**: `data/` directory used for samples and gitignored.
- [x] **V. Atomic Git Workflow**: Plan structured to support small, logical commits per task.

## Project Structure

### Documentation (this feature)

```text
specs/001-ocr-post-processing/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (CLI definition)
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
ocrpolish/
├── __init__.py
├── cli.py               # CLI entry point (argparse)
├── core.py              # Main processing logic
├── processor.py         # File-level transformations
└── utils/
    ├── __init__.py
    └── files.py         # Directory scanning and mirroring

tests/
├── __init__.py
├── conftest.py
├── integration/
│   └── test_cli.py
└── unit/
    ├── test_core.py
    └── test_processor.py

data/                    # Samples (gitignored)
```

**Structure Decision**: Single project structure as per Principle III and project requirements.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A       |            |                                     |
