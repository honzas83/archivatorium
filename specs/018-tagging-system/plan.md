# Implementation Plan: Precision Tagging System

**Branch**: `018-tagging-system` | **Date**: 2026-05-07 | **Spec**: [specs/018-tagging-system/spec.md](spec.md)
**Input**: Feature specification from `/specs/018-tagging-system/spec.md`

## Summary

Transition to a three-tiered, precise tagging system (Conceptual, Entity, Topic) using a two-pass architecture. Step 1 extracts primary metadata. Step 2 uses a dynamic tagging pass: single-pass for documents up to 32k tokens (leveraging `gemma4:31b`), and sliding window fallback for larger files, all using a non-thinking model configuration (`think: false`).

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: `click`, `ollama` (Python library), `pydantic`, `pyyaml`
**Storage**: Filesystem (Markdown frontmatter + Callout blocks)  
**Testing**: pytest, coverage  
**Target Platform**: CLI (cross-platform Python)
**Project Type**: Single project
**Performance Goals**: Target ~30-60 seconds for a single 32k context prefill/extraction on high-end GPUs.  
**Constraints**: Dynamic pass logic (Single vs Sliding Window), 32k token limit for `gemma4:31b`, non-thinking model config (`think: false`).
**Scale/Scope**: Use lightweight word-count heuristic with safety buffer for pre-pass decision.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

1. **Gate 1: Python Quality**: Ensure `ruff`, `mypy`, and `flake8` pass on all new code.
2. **Gate 2: CLI Interface**: Maintain existing `click` patterns for any new CLI flags.
3. **Gate 3: Recursive Processing**: New two-pass logic must maintain recursive directory structure mirroring.
4. **Gate 4: Data Isolation**: No large test documents should be added to the repo (use `data/` if needed).
5. **Gate 5: Atomic Git**: Tasks T001-T006 must be committed incrementally.

## Project Structure

### Documentation (this feature)

```text
specs/018-tagging-system/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Tasks definition
```

### Source Code (repository root)

```text
ocrpolish/
├── services/
│   ├── tagging_service.py   # New pass 2 logic (Dynamic: Single/Sliding)
│   ├── windowing_service.py # Sliding window implementation
│   └── topics_service.py    # Updated for hierarchical taxonomy
├── utils/
│   └── nlp.py               # Normalization, Deduplication, Token Counting
└── processor_metadata.py    # Refactored for two-pass workflow

tests/
├── unit/
└── integration/
```

**Structure Decision**: Single project structure within `ocrpolish/` and `tests/` as per constitution.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
