# Implementation Plan: Metadata Indexing

**Branch**: `015-metadata-indexing` | **Date**: 2026-05-04 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/015-metadata-indexing/spec.md`

## Summary
Implement an `index` subcommand for `ocrpolish` to generate Obsidian and XLSX indices from processed OCR metadata. The tool will parse YAML frontmatter and hierarchical tags within `[!abstract]` callouts, grouping entities into dedicated Markdown index pages and a consolidated spreadsheet.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: `click`, `pydantic`, `pyyaml`, `XlsxWriter` (New)  
**Storage**: Filesystem (input/output directories)  
**Testing**: `pytest`, `coverage`  
**Target Platform**: CLI (cross-platform Python)
**Project Type**: Single project
**Performance Goals**: Process 1,000 documents in < 10 seconds.
**Constraints**: Recursive processing, hashtag-based Obsidian indexing.
**Scale/Scope**: Local filesystem vault indexing.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Quality-Driven**: Ruff, Mypy, and Pytest are configured.
- **II. CLI-First**: Feature implemented as a CLI subcommand.
- **III. Recursive**: Supported via `--recursive` flag.
- **IV. Data Isolation**: Data stored in gitignored `data/`.
- **V. Atomic Git**: Commits will be task-based.

## Project Structure

### Documentation (this feature)

```text
specs/015-metadata-indexing/
├── plan.md              # This file
├── research.md          # Research findings
├── data-model.md        # Data models
├── quickstart.md        # Usage examples
├── contracts/           # CLI contract
│   └── cli-contract.md
└── tasks.md             # Implementation tasks
```

### Source Code (repository root)

```text
ocrpolish/
├── services/
│   └── indexing_service.py  # New: Core indexing logic
├── cli.py                   # Update: Add index subcommand
└── utils/
    └── metadata.py          # Update: Add abstract callout parser
```

**Structure Decision**: Single project structure as per project conventions. Core logic in `indexing_service.py`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | | |
