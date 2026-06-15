# Implementation Plan: Prompt Tag Normalization

**Branch**: `031-prompt-tag-normalization` | **Date**: 2026-06-12 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/031-prompt-tag-normalization/spec.md`

## Summary

Update the LLM prompt context used during metadata extraction so entity tags converge on canonical English/title-case forms, obvious OCR damage is corrected conservatively, relative filenames are available as contextual hints, and existing topic/conceptual tag behavior is preserved. The plan is driven by the v6 analysis findings in `COUNTS_v6.csv` and `docs/tag_analysis_report.md`, plus the requirement to include full source-relative filenames because archival code, document year, and related metadata can be encoded in paths. No schemas, CLI behavior, parsers, post-processing, taxonomy files, useful-tags files, or tests are to be changed.

## Technical Context

**Language/Version**: Python 3.12 (`requires-python = ">=3.12"`)

**Primary Dependencies**: Click CLI, Pydantic metadata/tagging models, PyYAML taxonomy/useful-tags loading, Ollama client integration, pytest/pytest-cov

**Storage**: Local filesystem Markdown/PDF vault output, YAML taxonomy/useful-tags files, generated XLSX metadata index; no storage changes for this feature

**Testing**: Existing pytest coverage may be run for regression only; do not add or modify test code for this feature unless the scope is explicitly changed

**Target Platform**: CLI on macOS and Linux

**Project Type**: Single Python CLI tool

**Performance Goals**: No measurable processing slowdown; prompt generation remains a single in-memory string assembly per tagging window and static taxonomy/useful-tags text continues to be cached as currently designed

**Constraints**: LLM prompt-context implementation; minimal plumbing may pass an existing source-relative filename into the prompt, but no schema, CLI option, taxonomy, useful-tags, output-format, migration, parser, post-processing, or test-code changes are allowed

**Scale/Scope**: Metadata processing for recursive document sets containing hundreds to thousands of Markdown/PDF-derived archive documents; validation uses representative excerpts matching v6 fragmentation findings

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **I. Quality-Driven Python Development**: Plan retains Python 3.12 and uses existing quality gates for regression only; it does not require adding or modifying test code.
- [x] **II. CLI-First Interface**: Existing `ocrpolish metadata` behavior remains the user-facing interface; no new non-CLI surface is introduced.
- [x] **III. Recursive Directory Processing**: Existing recursive metadata processing remains unchanged; prompt behavior applies uniformly to every processed document.
- [x] **IV. Data Isolation**: Validation may use sample excerpts derived from `COUNTS_v6.csv` and `docs/tag_analysis_report.md`; no real-world data files are moved into version control as part of this feature.
- [x] **V. Atomic Git Workflow**: Implementation should commit only LLM prompt/context changes relevant to this feature and must not stage unrelated untracked analysis files.

## Project Structure

### Documentation (this feature)

```text
specs/031-prompt-tag-normalization/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── tagging-prompt-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
ocrpolish/
├── services/
│   └── tagging_service.py        # LLM prompt context/content update
├── processor_metadata.py         # Pass source-relative filename into tagging prompt
└── models/
    └── metadata.py               # Existing output models; no planned changes

tests/
├── unit/
│   └── test_tagging_service.py   # Existing regression tests only; no planned edits
└── integration/
    └── test_metadata_command.py  # Existing regression tests only; no planned edits
```

**Structure Decision**: Keep the implementation to prompt context/content. `processor_metadata.py` may pass the existing source-relative filename into `TaggingService`; the CLI, schemas, metadata renderer, taxonomy files, useful-tags files, indexing, interlinking code, parser logic, and test code are out of scope.

## Complexity Tracking

No constitution violations or additional complexity are required.

## Phase 0: Research

Research decisions are recorded in [research.md](./research.md). All technical unknowns are resolved; no open clarification items remain.

## Phase 1: Design & Contracts

Design artifacts:

- [data-model.md](./data-model.md)
- [contracts/tagging-prompt-contract.md](./contracts/tagging-prompt-contract.md)
- [quickstart.md](./quickstart.md)

Post-design constitution re-check:

- [x] **I. Quality-Driven Python Development**: Artifacts rely on existing regression tests and standard project quality gates; no new or modified test code is planned.
- [x] **II. CLI-First Interface**: Contract preserves the existing `ocrpolish metadata` CLI behavior.
- [x] **III. Recursive Directory Processing**: No directory traversal behavior changes.
- [x] **IV. Data Isolation**: Validation references sample findings without committing local data outputs beyond existing analysis artifacts.
- [x] **V. Atomic Git Workflow**: Scope is bounded to this feature's spec/design plus later LLM prompt/context edits only.
