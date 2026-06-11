# Implementation Plan: Fix Tag and Interlink Bugs

**Branch**: `029-fix-tag-interlinks` | **Date**: 2026-06-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/029-fix-tag-interlinks/spec.md`

## Summary

Fix vault-generation metadata defects: generated organization and state entity tags with slash-containing names must be normalized into valid single-name tags; generated document-to-document interlinks must target filenames instead of vault-relative folder paths; topic extraction must retain every clearly justified taxonomy topic while using the top 100 resume-derived topic counter items as bounded prompt context. The implementation will update the existing tag parser, interlinking service, metadata tagging models, tagging prompt, and reuse-hint construction, then add focused unit and integration coverage around the reported examples.

## Technical Context

**Language/Version**: Python 3.12 (`requires-python = ">=3.12"`)

**Primary Dependencies**: Click CLI, Pydantic models, PyYAML, xlsxwriter, Ollama client integration, pytest/pytest-cov

**Storage**: Filesystem Markdown/PDF vault output; YAML taxonomy and useful-tags configuration files; generated XLSX metadata index

**Testing**: pytest with coverage; targeted unit tests plus integration/CLI validation

**Target Platform**: Local CLI processing on POSIX-style filesystems

**Project Type**: Python CLI application

**Performance Goals**: Preserve current single-pass parsing and interlinking behavior; keep tagging context bounded by top 100 topic counters so representative metadata parsing runs do not incur unbounded prompt growth

**Constraints**: Must keep recursive directory processing intact, must not touch real or sample data outside `data/`, must avoid unrelated working-tree changes, must keep generated Markdown links portable inside existing vault structure, and must keep topic counter hints subordinate to the approved taxonomy

**Scale/Scope**: Narrow bug fix covering generated organization/state tag parsing, filename-only generated document interlink targets, unlimited justified topic assignments, and top-100 topic counter hint context

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Quality-Driven Python Development**: PASS. Plan targets Python 3.12 code paths and includes pytest coverage, with final quality gates `ruff check .`, `ruff format .`, `flake8`, `mypy .`, and `pytest`.
- **CLI-First Interface**: PASS. Behavior remains exposed through the existing CLI workflows, especially metadata parsing during processing and `ocrpolish interlink`.
- **Recursive Directory Processing**: PASS. Interlink behavior must continue to operate across nested vault directories while producing filename-only generated document links.
- **Data Isolation**: PASS. Test fixtures may use temporary directories; no real sample data is required outside `data/`.
- **Atomic Git Workflow**: PASS. Implementation tasks should be committed in small, related increments and must not stage unrelated current working-tree changes.

## Project Structure

### Documentation (this feature)

```text
specs/029-fix-tag-interlinks/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── interlink-contract.md
│   └── tag-parser-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
ocrpolish/
├── models/
│   └── metadata.py
├── processor_metadata.py
├── services/
│   ├── tagging_service.py
│   └── interlinking_service.py
└── utils/
    └── tag_parser.py

tests/
├── integration/
│   ├── test_interlink_cli.py
│   └── test_tagging_pass.py
└── unit/
    ├── test_interlinking_service.py
    ├── test_processor_counters.py
    ├── test_tagging_service.py
    └── test_tag_parser.py
```

**Structure Decision**: Use the existing single-package CLI structure. The parser change belongs in `ocrpolish/utils/tag_parser.py`; generated document interlink target formatting belongs in `ocrpolish/services/interlinking_service.py`; topic limits and prompt guidance belong in `ocrpolish/models/metadata.py` and `ocrpolish/services/tagging_service.py`; top-100 reuse hints belong in `ocrpolish/processor_metadata.py`. Tests extend the existing unit and integration suites beside related coverage.

## Complexity Tracking

No constitution violations or added complexity are expected.

## Phase 0: Research

Research completed in [research.md](research.md). Decisions:

- Normalize slash-containing generated organization/state entity names before fixed-shape validation.
- Apply filename-only target formatting to all generated document-to-document interlinks.
- Preserve existing validation and warning behavior for malformed tags not fixed by slash normalization.
- Remove hard topic-assignment limits while keeping topic choices taxonomy-bound.
- Expand resume-derived topic counter context to the top 100 items while keeping context bounded.

## Phase 1: Design and Contracts

Design artifacts:

- [data-model.md](data-model.md)
- [contracts/tag-parser-contract.md](contracts/tag-parser-contract.md)
- [contracts/interlink-contract.md](contracts/interlink-contract.md)
- [contracts/topic-tagging-contract.md](contracts/topic-tagging-contract.md)
- [quickstart.md](quickstart.md)

Post-design constitution check:

- **Quality-Driven Python Development**: PASS. Artifacts define unit, integration, and full quality-gate validation.
- **CLI-First Interface**: PASS. Quickstart validates behavior through parser-level tests, tagging tests, metadata processing tests, and the `ocrpolish interlink` CLI path.
- **Recursive Directory Processing**: PASS. Contracts include nested vault path expectations for generated document links.
- **Data Isolation**: PASS. Quickstart uses temporary test directories and tracked tests only.
- **Atomic Git Workflow**: PASS. Scope remains limited to the affected parser, interlinking, tagging, metadata-model, and processor files plus focused tests/docs for this feature.
