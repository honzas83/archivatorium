# Implementation Plan: Obsidian Vault Interlinking

**Branch**: `020-obsidian-interlink-vault` | **Date**: 2026-05-07 | **Spec**: [specs/020-obsidian-interlink-vault/spec.md](spec.md)
**Input**: Feature specification from `/specs/020-obsidian-interlink-vault/spec.md`

## Summary
Implement a new `interlink` subcommand for `ocrpolish` to post-process Obsidian vaults in-place. The tool will build a global mapping of archive codes to file paths and then use this mapping to convert references (both in metadata callouts and body text) into clickable Markdown links, including cross-linking language versions.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: `click`, `pyyaml`, `pathlib`, `re`
**Storage**: Filesystem (in-place modification of Markdown files)
**Testing**: `pytest`, `coverage`  
**Target Platform**: CLI (cross-platform Python)
**Project Type**: Single project
**Performance Goals**: Process thousands of files within seconds (linear time complexity relative to file count).
**Constraints**: 
- Non-destructive: MUST NOT modify YAML frontmatter.
- Idempotent: MUST NOT nest links; replace existing ones instead.
- Target-specific: ONLY modify the "Metadata" callout table and the body text.
- Match Accuracy: Prefix-boundary matching with longest-match priority.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Quality-Driven**: OK (standard project stack)
- **II. CLI-First**: OK (new `interlink` command)
- **III. Recursive**: OK (recursive vault scanning)
- **IV. Isolation**: OK (no data in repo)
- **V. Atomic Git**: OK (task-based commits)

## Project Structure

### Documentation (this feature)

```text
specs/020-obsidian-interlink-vault/
├── plan.md              # This file
├── research.md          # Decisions and technical details
├── data-model.md        # Entities and state transitions
├── quickstart.md        # User guide and examples
├── contracts/
│   └── cli.md           # CLI interface contract
└── tasks.md             # Implementation tasks
```

### Source Code (repository root)

```text
ocrpolish/
├── cli.py               # Add 'interlink' command
├── services/
│   └── interlinking_service.py  # New: core logic for mapping and interlinking
└── utils/
    └── files.py         # File helpers (read/write)

tests/
├── integration/
│   └── test_interlink_cli.py   # CLI integration tests
└── unit/
    └── test_interlinking_service.py # Core logic unit tests
```

**Structure Decision**: Single project. The core logic will be encapsulated in a new `InterlinkingService` to keep the CLI thin and facilitate testing.

## Complexity Tracking

*No violations identified.*
