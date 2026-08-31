# Implementation Plan: Escape Non-Standard Hashtags in Vault

**Branch**: `034-escape-other-hashtags` | **Date**: 2026-07-29 | **Spec**: [specs/034-escape-other-hashtags/spec.md](spec.md)

**Input**: Feature specification from `specs/034-escape-other-hashtags/spec.md`

## Summary
To prevent non-standard hashtags (e.g. administrative markings like `#67-87155` or `#67-8`) from cluttering Obsidian's tag pane, the `interlink` command will run a regex-based selective escaping pass over document bodies to prefix these with a backslash `\`. Simultaneously, generated index notes (`Index - Tags.md` and `Index - Cities.md`, etc.) will be capped at 50 document links per key, appending a count and an Obsidian Search URI for any remaining entries to avoid Obsidian performance degradation on a 30k vault.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: `click`, `re`, `PyYAML`, `xlsxwriter`

**Storage**: Local Filesystem (in-place vault processing)

**Testing**: `pytest`

**Target Platform**: macOS

**Project Type**: CLI

**Performance Goals**: Processes a large vault (approx. 30k documents) without memory leakage or excessive CPU usage.

**Constraints**: Memory footprint must stay below 500MB during processing.

**Scale/Scope**: Vault scale is approximately 30,000 files.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Python 3.12 Development**: Yes. Follows standard conventions and uses `ruff` / `mypy` / `flake8` checks.
- **CLI-First**: Yes. Changes are integrated inside the existing CLI command (`archivatorium interlink`).
- **Data Isolation**: Yes. Real datasets are gitignored. Mock datasets are used for testing.
- **Atomic Git Workflow**: Yes. Logical commits will be made step-by-step.

*Status: **Passed***

## Project Structure

### Documentation (this feature)

```text
specs/034-escape-other-hashtags/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
└── quickstart.md        # Phase 1 output
```

### Source Code

```text
archivatorium/
├── services/
│   ├── interlinking_service.py # Hashtag escaping logic
│   └── indexing_service.py     # Index list capping logic
└── utils/
    └── tag_parser.py           # Uses CanonicalTagParser

tests/
└── unit/
    ├── test_interlinking_service.py # Tests for hashtag escaping
    └── test_indexing_service.py     # Tests for index page capping
```

**Structure Decision**: Monolith structure. Modifying the existing services (`interlinking_service.py` and `indexing_service.py`) and expanding their respective unit tests.

## Complexity Tracking

No violations of the project constitution. Structure and pattern decisions are fully aligned.

## Performance & Speed Optimizations

- **NFR-001 (Fast-path Substring Check)**: The function `escape_other_hashtags` checks `if "#" not in text: return text` before performing any string modifications. This completely skips processing on documents that have no hashtags.
- **NFR-002 (Procedural String Index Finder)**: Instead of executing a large regular expression or a character-by-character loop, the procedural parser utilizes C-optimized Python methods like `.find()`, `.count()`, and `.startswith()` with slice operations on a per-line basis, maintaining high efficiency.
- **Index I/O Reduction**: Group lists are capped to 50 entries to avoid serializing and writing massive files to disk, saving significant time during the indexing phase.
