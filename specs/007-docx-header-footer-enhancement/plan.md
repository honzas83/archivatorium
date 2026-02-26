# Implementation Plan: Improve DOCX Header and Footer Export

**Branch**: `007-docx-header-footer-enhancement` | **Date**: 2026-02-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-docx-header-footer-enhancement/spec.md`

## Summary

This feature improves the DOCX export by intelligently mapping Markdown markers to Word headers and footers. It introduces section-based page management in `python-docx` to isolate page-specific metadata, preserves "PDF Page N" footers across all pages, and migrates filtered lines near original page numbers (`-X-`) to the document margins.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: `python-docx`, `click`, `re`  
**Storage**: Filesystem (input/output directories)  
**Testing**: pytest, coverage  
**Target Platform**: CLI (cross-platform Python)
**Project Type**: Single project
**Performance Goals**: Negligible impact on processing time for standard document sizes.
**Constraints**: Recursive processing, directory mirroring, isolated DOCX sections.
**Scale/Scope**: Enhancement of the `DocxProcessor` in `ocrpolish/processor.py`.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Python 3.12 + `ruff` + `mypy` + `pytest` (Principle I)
- [x] CLI-First (Principle II)
- [x] Recursive processing maintained (Principle III)
- [x] Data isolation in `data/` (Principle IV)
- [x] Atomic commits per task (Principle V)

## Project Structure

### Documentation (this feature)

```text
specs/007-docx-header-footer-enhancement/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Research on python-docx and metadata proximity
├── data-model.md        # PageMetadata and DocxSection models
├── quickstart.md        # User guide for the new behavior
├── contracts/           # (Internal) API changes for processor
└── checklists/
    └── requirements.md  # Quality checklist
```

### Source Code (repository root)

```text
ocrpolish/
├── cli.py               # Argument handling (filters)
├── processor.py         # Main logic for DOCX generation
├── core.py              # Parsing logic
└── utils/
    └── docx_utils.py    # Helper for python-docx section styling
```

**Structure Decision**: Single project structure as per existing codebase.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*No violations.*
