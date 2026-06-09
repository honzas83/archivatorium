# Implementation Plan: Idempotent Vault Interlinking and Finalization

**Branch**: `025-idempotent-vault-interlink` | **Date**: 2026-06-09 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/025-idempotent-vault-interlink/spec.md`

## Summary

The objective is to consolidate the separate indexing, tagging, and interlinking phases of `ocrpolish` into a single, cohesive, and idempotent finalization command: `ocrpolish interlink VAULT_DIR`. This workflow scans the vault once into shared in-memory document records, performs in-place document interlinking (preventing nested links and duplicate table rows), updates/reparses modified files, and generates both Markdown index pages and a pivoted `metadata_index.xlsx` spreadsheet utilizing the `CanonicalTagParser`.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: `click`, `pyyaml`, `xlsxwriter`, `pydantic`

**Storage**: local filesystem (Obsidian vault markdown documents and sidecar files)

**Testing**: `pytest`

**Target Platform**: macOS / Linux / POSIX-compliant platforms

**Project Type**: CLI / Library

**Performance Goals**: Processes a 100-document vault under 10 seconds.

**Constraints**: Idempotency (zero byte diff on re-run), prevent link nesting (e.g. `[[ [[link]] ]]`), avoid duplicate references/language versions.

**Scale/Scope**: Operates solely in-place on the output `VAULT_DIR`.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Quality-Driven Python Development**: Passed. Using `ruff`, `flake8`, `mypy`, and `pytest`.
- **II. CLI-First Interface**: Passed. Unified CLI interface via `ocrpolish interlink VAULT_DIR`.
- **III. Recursive Directory Processing**: Passed. Recursively traverses the vault directory.
- **IV. Data Isolation**: Passed. Output indices/spreadsheets are written directly to `VAULT_DIR`.
- **V. Atomic Git Workflow**: Passed. Commits will be made in logical increments per task.

## Project Structure

### Documentation (this feature)

```text
specs/025-idempotent-vault-interlink/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
│   └── cli.md           # CLI Contract definition
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
ocrpolish/
├── cli.py               # Exposes the unified 'interlink' CLI command
├── models/
│   └── metadata.py      # Metadata and CanonicalTag schemas
├── services/
│   ├── interlinking_service.py  # Unified finalization orchestration & interlinking
│   └── indexing_service.py      # Markdown index and Excel spreadsheet generation
└── utils/
    ├── tag_parser.py    # Canonical tag parser
    └── metadata.py      # Frontmatter/callout parsers
```

**Structure Decision**: Single-project directory layout under `ocrpolish/` and `tests/`.

## Complexity Tracking

No constitution violations detected.
