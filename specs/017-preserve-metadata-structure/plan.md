# Implementation Plan: Preserve Metadata Directory Structure

**Branch**: `017-preserve-metadata-structure` | **Date**: 2026-05-06 | **Spec**: [specs/017-preserve-metadata-structure/spec.md](spec.md)
**Input**: Feature specification from `specs/017-preserve-metadata-structure/spec.md`

## Summary

This feature enhances the `metadata` command to replicate the source directory hierarchy in the output folder. It introduces an efficient mirroring strategy using hardlinks for non-markdown files and ensures robust UTF-8 handling for processed markdown documents. Additionally, it organizes mirrored PDFs into a `pdf/` subdirectory within each folder.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: `click` (CLI), `pathlib` (filesystem), `shutil` (copying), `os` (hardlinks)  
**Storage**: Filesystem (input/output directories)  
**Testing**: `pytest`  
**Target Platform**: CLI (cross-platform Python)
**Project Type**: Single project
**Performance Goals**: Minimize disk usage for non-markdown files via hardlinks. Ensure processing time is dominated by LLM calls, not filesystem operations.  
**Constraints**: Recursive processing, directory mirroring, strict UTF-8 output.
**Scale/Scope**: Handles deeply nested directory structures and thousands of files.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I (Quality)**: We will use `ruff`, `mypy`, and `pytest`. (Pass)
- **Principle III (Recursive Processing)**: This feature directly addresses and enhances recursive processing standards. (Pass)
- **Principle IV (Data Isolation)**: Input/Output directories are used; local data stays in `data/` or user-specified paths. (Pass)

## Project Structure

### Documentation (this feature)

```text
specs/017-preserve-metadata-structure/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── checklists/
    └── requirements.md  # Spec quality checklist
```

### Source Code (repository root)

```text
ocrpolish/
├── cli.py               # Updated 'metadata' command
├── processor_metadata.py # Updated 'process_directory' and mirroring logic
└── utils/
    └── metadata.py      # Robust UTF-8 reading/writing helpers
```

**Structure Decision**: Single project structure (Option 1). We will modify existing modules to support the new mirroring behavior.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |
