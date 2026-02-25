# Implementation Plan: DOCX Generation with Page Mirroring

**Branch**: `005-docx-generation` | **Date**: 2026-02-25 | **Spec**: [specs/005-docx-generation/spec.md]
**Input**: Feature specification from `/specs/005-docx-generation/spec.md`

## Summary

The goal is to add a `--docx` flag to the `ocrpolish` CLI that generates a DOCX document mirroring the page structure of the processed Markdown files. The implementation will use the `python-docx` library to create Word documents, inserting page breaks at `---` and `# Page X` markers. All text will be rendered in a fixed-width font (Consolas) to maintain a typewriter-like aesthetic without using Courier New.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: `python-docx` (New), `argparse`, `pathlib`  
**Storage**: Filesystem (input/output directories)  
**Testing**: pytest, coverage  
**Target Platform**: CLI (cross-platform Python)
**Project Type**: Single project
**Performance Goals**: DOCX generation should add <20% overhead to file processing.
**Constraints**: Recursive processing, directory mirroring, 1:1 page mapping.
**Scale/Scope**: Handles individual files up to 1000 pages (typical OCR batch).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I (Quality)**: Use `ruff`, `mypy`, `pytest`. (Pass: Standards are already in place).
- **Principle II (CLI-First)**: New flag `--docx` follows POSIX style. (Pass).
- **Principle III (Recursive)**: DOCX files will be placed in the mirrored output directory structure. (Pass).
- **Principle IV (Data Isolation)**: Tests will use the `data/` directory. (Pass).
- **Principle V (Atomic Git)**: Implementation will be broken into small, logical tasks. (Pass).

## Project Structure

### Documentation (this feature)

```text
specs/005-docx-generation/
├── plan.md              # This file
├── research.md          # Research findings
├── data-model.md        # Entities and validation rules
├── quickstart.md        # Integration guide
└── contracts/           
    └── cli.md           # CLI argument changes
```

### Source Code (repository root)

```text
ocrpolish/
├── cli.py               # Update argparse to include --docx
├── core.py              # Update run_processing to handle DOCX flag
├── data_model.py        # Add docx_enabled to ProcessingConfig
├── processor.py         # Add DOCX generation logic
└── utils/
    └── docx_utils.py    # (NEW) Helper for python-docx operations

tests/
├── integration/
│   └── test_docx_generation.py  # (NEW) Verify end-to-end DOCX creation
└── unit/
    └── test_docx_utils.py       # (NEW) Test font and page break logic
```

**Structure Decision**: Single project. Added `utils/docx_utils.py` to encapsulate the third-party dependency logic and keep `processor.py` clean.

## Complexity Tracking

*No constitution violations identified.*
