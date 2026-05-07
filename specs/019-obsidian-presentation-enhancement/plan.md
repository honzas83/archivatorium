# Implementation Plan: Obsidian Presentation Enhancement

**Branch**: `019-obsidian-presentation-enhancement` | **Date**: 2026-05-07 | **Spec**: [specs/019-obsidian-presentation-enhancement/spec.md](specs/019-obsidian-presentation-enhancement/spec.md)
**Input**: Feature specification from `/specs/019-obsidian-presentation-enhancement/spec.md`

## Summary

This feature improves the presentation of OCR-processed documents in Obsidian by automatically configuring the output vault and adding visual metadata callouts. The technical approach involves copying reference configuration files (`app.json`, `appearance.json`, `CONTENT.base`) and updating the markdown generation logic to include formatted callouts (Metadata, Abstract, Citations) with updated BibTeX and topic citation normalization.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: `click`, `pydantic`, `ollama`, `python-docx` (existing)
**Storage**: Filesystem (input/output directories)  
**Testing**: `pytest`, `coverage`  
**Target Platform**: CLI (cross-platform Python)
**Project Type**: Single project
**Performance Goals**: Minimal overhead on existing processing time.
**Constraints**: Recursive processing, directory mirroring, preservation of existing metadata structure.
**Scale/Scope**: Document-level enhancements for all processed markdown files.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Quality**: Implementation must pass `ruff`, `mypy`, and `pytest` with coverage. (✅)
- **Interface**: Feature must be integrated into the existing `ocrpolish` CLI. (✅)
- **Structure**: Must maintain recursive directory processing and structure mirroring. (✅)
- **Isolation**: Reference data `nato_npg_metadata.v4` is correctly ignored in `.gitignore`. (✅)
- **Workflow**: Each logical task will be committed atomically. (✅)

## Project Structure

### Documentation (this feature)

```text
specs/019-obsidian-presentation-enhancement/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (generated later)
```

### Source Code (repository root)

```text
ocrpolish/
├── services/
│   ├── tagging_service.py   # Update for Topic citation normalization
│   └── indexing_service.py  # Potential site for vault initialization
├── utils/
│   └── metadata.py          # Update for Callout generation logic
└── cli.py                   # Update for vault init triggers

tests/
├── integration/
└── unit/
```

**Structure Decision**: Single project structure as per Principle I.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

*(No violations identified)*
