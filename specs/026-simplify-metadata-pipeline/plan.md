# Implementation Plan: Simplify Metadata Pipeline

**Branch**: `026-simplify-metadata-pipeline` | **Date**: 2026-06-09 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/026-simplify-metadata-pipeline/spec.md`

## Summary

Simplify production metadata processing so the canonical metadata command requires explicit hierarchy and tags files, defaults vault/PDF roots to the output directory, always mirrors PDFs into `pdf/`, and generates source links from the output vault layout. Remove obsolete non-flat topic extraction from production runtime/tests, make the flat `TaggingService` path the only production mode, refactor `MetadataProcessor.process_file` into explicit testable stages, and precompute static taxonomy/useful-tag prompt text once per tagging service instance.

## Technical Context

**Language/Version**: Python 3.12 (`requires-python = ">=3.12"`)

**Primary Dependencies**: Click CLI, Pydantic models, PyYAML, Ollama client integration, pytest/pytest-cov

**Storage**: Filesystem Markdown/PDF vault output; YAML configuration files for taxonomy and useful tags

**Testing**: pytest with coverage; focused unit tests for processing stages and tagging prompt reuse; integration tests for CLI output layout and compatibility

**Target Platform**: Local/automated command-line environments that can run Python and access source/output directories

**Project Type**: Single Python CLI package

**Performance Goals**: Static taxonomy/useful-tag prompt sections are built once per `TaggingService` instance; no per-window YAML taxonomy dump or static prompt rebuild during sliding-window tagging

**Constraints**: Preserve compatible metadata output, recursive mirrored source structure, Obsidian vault initialization, callout ordering, citation generation, page counting from page headers, and interlinking compatibility

**Scale/Scope**: Production metadata runs over recursive document directories containing Markdown sources and source PDFs, including large documents that require multiple tagging windows

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Quality-Driven Python Development**: PASS. Plan uses Python 3.12, pytest, coverage, ruff, flake8, and mypy gates.
- **II. CLI-First Interface**: PASS. Primary behaviour is exposed through the existing `metadata` CLI command.
- **III. Recursive Directory Processing**: PASS. Plan preserves recursive Markdown discovery and mirrored output structure.
- **IV. Data Isolation**: PASS. Quickstart uses temporary/sample data only; no real data is added to version control.
- **V. Atomic Git Workflow**: PASS. Implementation tasks must be scoped to relevant files and committed in small logical increments.

## Project Structure

### Documentation (this feature)

```text
specs/026-simplify-metadata-pipeline/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── metadata-command.md
└── tasks.md
```

### Source Code (repository root)

```text
ocrpolish/
├── cli.py                         # metadata command defaults, required options, flat-only wiring
├── processor_metadata.py          # staged metadata file pipeline and PDF/source-link behaviour
├── services/
│   ├── tagging_service.py         # flat production tagging and prompt precomputation
│   ├── flattening_service.py      # taxonomy flattening reused by tagging service
│   └── topics_service.py          # remove from production runtime path
├── models/
│   ├── metadata.py                # metadata/tagging schemas used by pipeline
│   └── topics.py                  # evaluate/remove production-only legacy topic schemas as needed
└── utils/
    ├── metadata.py                # rendering, reconciliation, citation, mirror helpers
    └── tag_parser.py              # generated output tag ingestion

tests/
├── integration/
│   ├── test_metadata_command.py
│   ├── test_pdf_subdirectory.py
│   ├── test_obsidian_metadata.py
│   ├── test_vault_init.py
│   └── test_flat_extraction.py
└── unit/
    ├── test_metadata_processor.py
    ├── test_metadata_stripping.py
    ├── test_reconciliation.py
    ├── test_tagging_service.py
    ├── test_flattening.py
    └── test_processor_counters.py

scripts/evaluation/ or evaluation/
└── legacy topic extraction evaluation scripts, if retained outside `ocrpolish/`
```

**Structure Decision**: Keep the existing single-package CLI structure. Runtime changes stay in `ocrpolish/`; production tests stay under `tests/unit` and `tests/integration`; any retained legacy evaluation path moves outside the package runtime path.

## Phase 0 Research

Resolved in [research.md](research.md).

Key decisions:
- Default omitted `vault_root` and `pdf_dir` to `output_dir`, but generate source links from the mirrored vault PDF path.
- Remove non-flat production topic extraction instead of keeping a hidden or deprecated runtime switch.
- Refactor `process_file` into named stage methods returning explicit stage result data.
- Precompute flattened taxonomy and static prompt sections in `TaggingService.__init__`.

## Phase 1 Design

Design artifacts:
- [data-model.md](data-model.md)
- [contracts/metadata-command.md](contracts/metadata-command.md)
- [quickstart.md](quickstart.md)

## Post-Design Constitution Check

- **I. Quality-Driven Python Development**: PASS. Artifacts define focused unit/integration coverage and existing quality gates.
- **II. CLI-First Interface**: PASS. CLI contract is explicit and remains POSIX-style.
- **III. Recursive Directory Processing**: PASS. Mirrored structure and recursive directory handling are preserved.
- **IV. Data Isolation**: PASS. Validation uses temporary/sample data paths and does not require committed real data.
- **V. Atomic Git Workflow**: PASS. Design supports small commits by separating CLI defaults, pipeline stages, tagging optimization, legacy removal, and regression tests.

## Complexity Tracking

No constitution violations.
