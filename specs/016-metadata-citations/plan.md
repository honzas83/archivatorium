# Implementation Plan: Metadata Citations

**Branch**: `016-metadata-citations` | **Date**: 2026-05-06 | **Spec**: [specs/016-metadata-citations/spec.md](spec.md)
**Input**: Feature specification from `/specs/016-metadata-citations/spec.md`

## Summary

Implement automated citation blocks at the end of generated Obsidian Markdown files. The system will append a standardized callout containing Chicago, Harvard, and BibTeX citation styles, derived from document metadata. The implementation will involve updating `MetadataProcessor` to generate and append this citation callout during the file processing workflow.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: `click`, `pathlib`, `typing`, `pydantic`, `PyYAML`  
**Storage**: Filesystem (input/output directories)  
**Testing**: `pytest`, `coverage`  
**Target Platform**: CLI (cross-platform Python)
**Project Type**: Single project
**Performance Goals**: < 100ms overhead per document  
**Constraints**: Recursive processing, directory mirroring, Obsidian callout syntax
**Scale/Scope**: All documents processed by the `metadata` command.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I: Quality-Driven Python Development**: PASS (using Python 3.12, ruff, mypy, pytest)
- **Principle II: CLI-First Interface**: PASS (integrated into `metadata` CLI command)
- **Principle III: Recursive Directory Processing**: PASS (utilizes existing `MetadataProcessor` recursive logic)
- **Principle IV: Data Isolation**: PASS (no sensitive data committed; using existing `data/` patterns)
- **Principle V: Atomic Git Workflow**: PASS (tasks will be committed logical increments)

## Project Structure

### Documentation (this feature)

```text
specs/016-metadata-citations/
├── plan.md              # This file
├── research.md          # Research findings
├── data-model.md        # Citation data structure
├── quickstart.md        # Usage guide
└── checklists/
    └── requirements.md  # Spec quality checklist
```

### Source Code (repository root)

```text
ocrpolish/
├── processor_metadata.py  # MAIN: Append citation callout in process_file
└── utils/
    └── metadata.py        # ADD: Citation formatting utilities

tests/
├── unit/
│   └── test_citations.py  # NEW: Unit tests for citation formatting
└── integration/
    └── test_metadata_citations.py # NEW: Verify citations in generated MD
```

**Structure Decision**: Single project structure (Option 1). Integrated into existing core services and utilities.

## Complexity Tracking

*No violations identified.*
