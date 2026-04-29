# Implementation Plan: LLM Flat Topic Extraction

**Branch**: `012-llm-flat-topic-extraction` | **Date**: 2026-04-29 | **Spec**: `/specs/012-llm-flat-topic-extraction/spec.md`
**Input**: Feature specification from `/specs/012-llm-flat-topic-extraction/spec.md`

## Summary

Implement a single-step topic extraction service that flattens a nested Category/Topic hierarchy into a YAML format with positive and negative samples. This approach allows the LLM to use the full context of the hierarchy for better classification accuracy, replacing the multi-step "narrowing" process.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: `ollama`, `pydantic`, `pyyaml`, `click`  
**Storage**: Filesystem (input/output directories)  
**Testing**: `pytest`, `coverage`  
**Target Platform**: CLI (cross-platform Python)
**Project Type**: Single project
## Performance Goals: Process up to 100 topics; accuracy improvement > 15%.
**Constraints**: Recursive processing, directory mirroring, token limits.
**Scale/Scope**: Single pass extraction with full sample context.


## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Python 3.12: Development will be in Python 3.12.
- [x] CLI-First: Feature will be integrated into the existing CLI.
- [x] Recursive Processing: Will maintain existing recursive directory support.
- [x] Data Isolation: Test data will reside in `data/` or be mocked.
- [x] Atomic Git: Commits will be logical and small.
- [x] Quality Gates: `ruff`, `mypy`, `pytest` will be used.

## Project Structure

### Documentation (this feature)

```text
specs/012-llm-flat-topic-extraction/
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
│   ├── topics_service.py     # Update to support flat extraction
│   └── flattening_service.py # NEW: Logic for hierarchy linearization
├── models/
│   ├── topics.py             # Update models for samples and flat format
├── cli.py                    # Update CLI with new options
└── core.py                   # Orchestration

tests/
├── integration/
│   └── test_flat_extraction.py
└── unit/
    ├── test_flattening.py
    └── test_topics_service_updates.py
```

**Structure Decision**: Single project structure as per core guidelines. Extending existing `services` and `models` modules.

## Complexity Tracking

*No violations identified.*
