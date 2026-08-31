# Implementation Plan: Normalize Qwen 3.8 OCR Output

**Branch**: `037-qwen38-ocr-cleanup` | **Date**: 2026-08-31 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/037-qwen38-ocr-cleanup/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Normalize every successful OCR response before it reaches page context or Markdown output. A pure text-normalization step will discard content through the final exact `</think>` marker, remove separator blank lines left by that marker, and remove the minimum shared ASCII-space indentation from nonblank lines while preserving relative indentation. Each per-PDF OCR run will use a monotonic clock and count every non-skipped input page once, logging total elapsed processing time and average seconds per attempted page from a `finally` path so retries and failed attempts remain represented.

## Technical Context

**Language/Version**: Python 3.12 (`requires-python = ">=3.12"`)

**Primary Dependencies**: Python standard-library text and timing facilities, Click CLI, official Ollama Python client, httpx, PyPDF2, pdf2image

**Storage**: Existing local PDF input and Markdown output; no new persisted data or metadata

**Testing**: pytest and pytest-cov with mocked Ollama responses, mocked monotonic time, and temporary PDF/Markdown paths

**Target Platform**: macOS and Linux CLI clients connecting to a local or remote Ollama host

**Project Type**: Single-project command-line application

**Performance Goals**: Normalize each response in one linear pass without extra model requests or page renders; add negligible work compared with remote OCR; report timing to millisecond precision

**Constraints**: Cleanup applies to every selected OCR model and mode; the marker match is exact and case-sensitive; tabs or mixed tab/space indentation prevent dedenting; retry, resume, ordering, model selection, filenames, and error handling remain unchanged

**Scale/Scope**: Existing recursive batches of hundreds of multipage PDFs; changes are limited to OCR response normalization, per-PDF run metrics, focused tests, and feature documentation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Quality-Driven Python Development — PASS**: The design stays in Python 3.12, uses a small typed normalization boundary, and assigns focused unit and integration coverage. Implementation must pass `ruff check .`, `ruff format --check .`, `flake8`, `mypy .`, `pytest`, and coverage reporting.
- **II. CLI-First Interface — PASS**: Operators receive normalized Markdown and timing information through the existing `archivatorium ocr` command and its existing logs; no secondary interface is introduced.
- **III. Recursive Directory Processing — PASS**: Recursive PDF discovery and mirrored Markdown output remain unchanged. Normalization and timing occur inside the existing per-document processing path.
- **IV. Data Isolation — PASS**: Automated tests use mocks and temporary paths. No real documents, model responses, or binary fixtures are added to version control.
- **V. Atomic Git Workflow — PASS**: Implementation can be split into focused normalization, metrics, test, and documentation commits while excluding unrelated working-tree files.

**Pre-design gate result**: PASS. No constitutional violations or unresolved clarifications.

## Project Structure

### Documentation (this feature)

```text
specs/037-qwen38-ocr-cleanup/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 decisions
├── data-model.md        # Phase 1 transient data definitions
├── quickstart.md        # Phase 1 validation guide
├── contracts/
│   └── ocr-output.md    # Observable normalization and logging contract
└── tasks.md             # Phase 2 output (/speckit-tasks command - not created here)
```

### Source Code (repository root)

```text
archivatorium/
└── ocr_engine.py                # Response normalization and per-PDF timing summary

tests/
├── unit/
│   └── test_ocr_engine.py       # Pure normalization, retry, resume, and timing tests
└── integration/
    └── test_ocr_cli.py          # Saved output and visible logging behavior
```

**Structure Decision**: Extend the existing OCR engine because it is already the single boundary between raw model responses and page text, and its `run_ocr` method owns the per-PDF lifecycle. No new service, CLI option, storage format, or dependency is needed.

## Complexity Tracking

No constitutional violations require justification.

## Post-Design Constitution Check

- **I. Quality-Driven Python Development — PASS**: The design defines deterministic, independently testable normalization and timing rules and retains all required quality gates.
- **II. CLI-First Interface — PASS**: The output and timing contract is observable through the existing OCR command without a new interface.
- **III. Recursive Directory Processing — PASS**: The contract preserves recursive discovery, mirrored output, resume skips, and page order.
- **IV. Data Isolation — PASS**: The quickstart uses disposable paths and automated checks use mocked responses and temporary files.
- **V. Atomic Git Workflow — PASS**: All planned production and test changes are confined to the identified OCR files and feature artifacts.

**Post-design gate result**: PASS. Phase 1 introduces no constitutional violations.
