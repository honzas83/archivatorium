# Implementation Plan: Item Type Metadata

**Branch**: `032-item-type-metadata` | **Date**: 2026-06-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/032-item-type-metadata/spec.md`

## Summary

Add a leading `item_type` field to generated archival metadata so every newly generated or regenerated item is classified with one value from the approved closed document-form vocabulary. The implementation will extend the existing metadata extraction model and prompt guidance, preserve backward readability for older records, place the field first in generated frontmatter and metadata callouts, and add the field to structured review/export output.

## Technical Context

**Language/Version**: Python 3.12 (`requires-python = ">=3.12"`)

**Primary Dependencies**: Click CLI, Pydantic metadata models, PyYAML frontmatter handling, xlsxwriter/openpyxl-backed export verification, Ollama client integration, pytest/pytest-cov

**Storage**: Local filesystem Markdown/PDF vault output with YAML frontmatter and generated XLSX metadata index; no new storage backend

**Testing**: pytest unit and integration coverage for schema defaults, prompt text, frontmatter ordering, metadata callouts, and XLSX export

**Target Platform**: CLI on macOS and Linux

**Project Type**: Single Python CLI tool

**Performance Goals**: No measurable processing slowdown beyond one additional scalar field in the existing metadata extraction response and output rendering paths

**Constraints**: Preserve existing CLI options and recursive processing behavior; keep historical metadata readable; use a closed vocabulary; do not change taxonomy/useful-tags files or canonical tag behavior

**Scale/Scope**: Metadata processing for recursive document sets containing hundreds to thousands of Markdown/PDF-derived archive documents; item type appears in every newly generated or regenerated metadata record and generated metadata index

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **I. Quality-Driven Python Development**: Plan retains Python 3.12 and requires targeted pytest coverage for model, prompt, rendering, and export behavior.
- [x] **II. CLI-First Interface**: Existing `ocrpolish metadata` and `ocrpolish finalize` workflows remain the user-facing interface; no new UI or service surface is introduced.
- [x] **III. Recursive Directory Processing**: Existing recursive metadata processing remains unchanged; the new field is produced for every processed Markdown document in the current traversal flow.
- [x] **IV. Data Isolation**: Validation uses synthetic fixtures under pytest temporary directories; no sample or real-world data is added to version control.
- [x] **V. Atomic Git Workflow**: Implementation scope is limited to metadata schema, prompt, rendering/export surfaces, and relevant tests; unrelated untracked analysis files must not be staged.

## Project Structure

### Documentation (this feature)

```text
specs/032-item-type-metadata/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── metadata-item-type-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
ocrpolish/
├── models/
│   └── metadata.py              # item_type field and allowed-value constraint
├── processor_metadata.py        # metadata prompt guidance and leading frontmatter/order handling
└── services/
    └── indexing_service.py      # XLSX metadata index includes item type

tests/
├── unit/
│   ├── test_metadata_schema.py      # item_type default and validation
│   ├── test_metadata_processor.py   # prompt guidance and output field order
│   └── test_xlsx_export.py          # metadata index column/value
└── integration/
    └── test_metadata_command.py     # generated output includes item_type end-to-end if existing patterns fit
```

**Structure Decision**: Keep the implementation inside the existing Python CLI metadata pipeline. No new command, package, taxonomy file, useful-tags file, or storage layout is required.

## Complexity Tracking

No constitution violations or additional complexity are required.

## Phase 0: Research

Research choices are recorded in [research.md](./research.md). All technical unknowns are resolved; no open clarification items remain.

## Phase 1: Design & Contracts

Design artifacts:

- [data-model.md](./data-model.md)
- [contracts/metadata-item-type-contract.md](./contracts/metadata-item-type-contract.md)
- [quickstart.md](./quickstart.md)

Post-design constitution re-check:

- [x] **I. Quality-Driven Python Development**: Design includes focused pytest coverage for all changed behavior and keeps existing quality gates applicable.
- [x] **II. CLI-First Interface**: The plan preserves the CLI workflow and changes only generated metadata content.
- [x] **III. Recursive Directory Processing**: The field is added inside per-file metadata extraction/rendering and therefore applies uniformly during recursive processing.
- [x] **IV. Data Isolation**: Quickstart and tests rely on synthetic temporary fixtures only.
- [x] **V. Atomic Git Workflow**: Artifacts and planned implementation files are feature-specific; unrelated untracked files remain outside the planned commit scope.
