# Implementation Plan: Metadata Correctness Fixes

**Branch**: `027-fix-metadata-correctness` | **Date**: 2026-06-09 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/027-fix-metadata-correctness/spec.md`

## Summary

Fix remaining correctness gaps in the existing metadata pipeline without changing the canonical tag model or adding new commands. Align resume preflight with generated-document discovery, prevent double-counting skipped outputs, feed rebuilt canonical counters into the existing tagging pass, make conceptual tag extraction mandatory for substantive documents, preserve hierarchical conceptual tag paths, remove legacy index/export fallbacks, and make metadata mask, dry-run, and per-folder PDF mirroring behaviour match user intent.

## Technical Context

**Language/Version**: Python 3.12 (`requires-python = ">=3.12"`)

**Primary Dependencies**: Click CLI, Pydantic models, PyYAML, xlsxwriter, Ollama client integration, pytest/pytest-cov

**Storage**: Filesystem Markdown/PDF vault output; YAML taxonomy and useful-tags configuration files; generated XLSX metadata index

**Testing**: pytest with focused unit, integration, and existing coverage gates

**Target Platform**: Local and automated command-line environments that can run Python and access recursive source/output directories

**Project Type**: Single Python CLI package

**Performance Goals**: Resume-derived reuse hints remain compact, bounded to top counters; generated-document preflight scans avoid known support/template folders and files

**Constraints**: Preserve the existing canonical tag model, `TaggingService` production path, metadata command, finalization/interlinking compatibility, generated output format, hierarchical `#Tags/...` conceptual paths, per-generated-folder `pdf/` source mirroring, source-tree mirroring compatibility where not contradicted by dry-run/mask safety, and LLM prompt stripping of generated sections

**Scale/Scope**: Recursive archival Markdown/PDF directories and generated Obsidian vaults containing document outputs, support files, index pages, templates, sidecars, and metadata exports

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Quality-Driven Python Development**: PASS. Plan uses Python 3.12, pytest, coverage, ruff, flake8, and mypy gates.
- **II. CLI-First Interface**: PASS. User-facing behaviour remains exposed through existing CLI commands, especially `metadata`, `index`, and `interlink`.
- **III. Recursive Directory Processing**: PASS. Plan preserves recursive directory traversal while correcting which files are eligible for enrichment and counter rebuilding.
- **IV. Data Isolation**: PASS. Validation uses temporary fixtures only; no real archival data is added to version control.
- **V. Atomic Git Workflow**: PASS. Work is separable into resume scanning, tagging validation, indexing/export, and CLI safety commits.

## Project Structure

### Documentation (this feature)

```text
specs/027-fix-metadata-correctness/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── metadata-correctness.md
└── tasks.md
```

### Source Code (repository root)

```text
ocrpolish/
├── cli.py                         # metadata mask/dry-run safety; index/interlink export wiring
├── processor_metadata.py          # generated-document preflight, skip counting, reuse hints, per-folder PDF mirroring, dry-run/mask orchestration
├── models/
│   └── metadata.py                # explicit tagging result schemas and validation expectations
├── services/
│   ├── tagging_service.py         # mandatory conceptual tags, non-substantive classifier, reuse hints, prompt/schema handling
│   ├── indexing_service.py        # canonical-only indexing and XLSX export
│   └── interlinking_service.py    # generated-document discovery/exclusion contract to share or mirror
└── utils/
    ├── metadata.py                # generated-section stripping remains source for LLM-safe content
    ├── nlp.py                     # conceptual tag filtering and generic duplicate suppression rules
    └── tag_parser.py              # canonical tag parsing, including hierarchical #Tags paths, remains authoritative

tests/
├── integration/
│   ├── test_metadata_command.py   # metadata mask and dry-run CLI behaviour
│   ├── test_resume_safety.py      # resume preflight and skip counting over mixed vaults
│   ├── test_obsidian_metadata.py  # full generated output regressions
│   └── test_interlink_cli.py      # finalization/index export canonical-only regressions
└── unit/
    ├── test_metadata_processor.py # generated-document eligibility and LLM prompt stripping
    ├── test_processor_counters.py # exact-once counter updates and reuse hint construction
    ├── test_tagging_service.py    # conceptual tag schema, validation, prompts, classifier
    ├── test_nlp_normalization.py  # duplicate suppression preservation
    ├── test_indexing_service.py   # canonical-only Markdown index behaviour
    ├── test_xlsx_export.py        # canonical-only spreadsheet export behaviour
    └── test_tag_parser.py         # canonical parser regression coverage
```

**Structure Decision**: Keep all runtime work in the existing `ocrpolish/` package and all validation in existing `tests/unit` and `tests/integration` suites. No new package, metadata model, tag model, or finalization command is introduced.

## Phase 0 Research

Resolved in [research.md](research.md).

Key decisions:
- Reuse one generated-document eligibility rule across resume, interlinking, finalization, indexing inputs, and tests.
- Keep canonical tag parsing strict and remove legacy fallback migration from indexing/export.
- Treat conceptual tag presence as a tagging-quality contract for substantive documents, enforced after structured parsing.
- Preserve hierarchical conceptual tag paths such as `#Tags/WINTEX/73` as canonical `#Tags/...` data.
- Use deterministic non-substantive administrative-stub detection before accepting empty conceptual tags.
- Feed resume counters into tagging as compact preferred-vocabulary hints, not as replacement taxonomy.
- Make metadata dry-run non-mutating at the CLI orchestration boundary.
- Mirror source PDFs into the local `pdf/` directory beside each generated Markdown output.

## Phase 1 Design

Design artifacts:
- [data-model.md](data-model.md)
- [contracts/metadata-correctness.md](contracts/metadata-correctness.md)
- [quickstart.md](quickstart.md)

## Post-Design Constitution Check

- **I. Quality-Driven Python Development**: PASS. Design defines unit and integration coverage plus existing quality gates.
- **II. CLI-First Interface**: PASS. Contracts describe existing CLI behaviour rather than new user commands.
- **III. Recursive Directory Processing**: PASS. Recursive handling is preserved with corrected eligibility and safety semantics.
- **IV. Data Isolation**: PASS. Quickstart scenarios rely on temporary fixture data and committed test fixtures only.
- **V. Atomic Git Workflow**: PASS. Design supports small commits by isolating resume discovery, tagging validation, indexing/export cleanup, and CLI safety changes.

## Complexity Tracking

No constitution violations.
