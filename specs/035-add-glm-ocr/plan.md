# Implementation Plan: Add GLM OCR Mode

**Branch**: `035-add-glm-ocr` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/035-add-glm-ocr/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add `--mode {standard,glm}` to the existing OCR command with `standard` as the default and unchanged existing behavior. The engine will resolve a small immutable mode profile that owns prompt construction, previous-page context policy, thinking control, and inference defaults, but never model selection. GLM requests will use a single `Text Recognition:` user message with the page image, send `think: false` and six required values—including `repeat_last_n=512` to cover longer repeated passages—to the remote Ollama `/api/chat` endpoint, and suppress neighboring-page OCR context on initial, resumed, and retried recognition. Optional CLI overrides will merge over the selected profile without introducing a new configuration-file subsystem.

## Technical Context

**Language/Version**: Python 3.12 (`requires-python = ">=3.12"`)

**Primary Dependencies**: Click CLI, official Ollama Python client as transport to the remote Ollama API, httpx, PyPDF2, pdf2image

**Storage**: Local PDF input and Markdown output; no new persisted data or mode metadata

**Testing**: pytest and pytest-cov with mocked Ollama API calls and temporary PDF/Markdown fixtures

**Target Platform**: macOS and Linux CLI clients connecting to a local or remote Ollama API host

**Project Type**: Single-project command-line application

**Performance Goals**: Preserve the current one API request per page requiring recognition, skip already recognized pages, and add no extra model calls or page renders for mode resolution

**Constraints**: No-mode request shape and behavior remain unchanged; GLM pages never receive neighboring OCR text; mode never selects a model; retries reuse the same isolated request; the remote Ollama API is the inference contract; GLM mode requires a remote server that supports `think: false` (Ollama 0.9.0 or newer)

**Scale/Scope**: Existing recursive batches of hundreds of multipage PDFs; changes limited to OCR CLI/options, request construction, tests, and user documentation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Quality-Driven Python Development — PASS**: The design uses Python 3.12 and adds focused unit/integration coverage. Implementation must pass `ruff check .`, `ruff format --check .`, `flake8`, `mypy .`, `pytest`, and coverage reporting.
- **II. CLI-First Interface — PASS**: The capability is exposed as the POSIX-style `--mode {standard,glm}` flag plus explicit inference override options on the existing command.
- **III. Recursive Directory Processing — PASS**: Existing recursive PDF discovery and mirrored Markdown output remain unchanged; the feature alters only per-page API request behavior.
- **IV. Data Isolation — PASS**: Tests use mocks and temporary paths. No real documents, model output, or binary fixtures are added outside the gitignored `data/` area.
- **V. Atomic Git Workflow — PASS**: Implementation can be divided into profile/request logic, CLI integration, tests, and documentation commits without staging unrelated pre-existing worktree changes.

**Pre-design gate result**: PASS. No constitutional violations or unresolved clarifications.

## Project Structure

### Documentation (this feature)

```text
specs/035-add-glm-ocr/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/
│   └── cli.md           # OCR CLI and remote API request contract
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
archivatorium/
├── cli.py                       # Add mode and inference override options
├── ocr_engine.py                # Resolve profiles and construct API requests
└── markdown_parser.py           # Existing resume parser; no production change expected

tests/
├── integration/
│   └── test_ocr_cli.py          # CLI parsing, propagation, and compatibility
└── unit/
    └── test_ocr_engine.py       # Exact request, context, retry, and resume behavior

README.md                        # Document opt-in mode and override options
pyproject.toml                   # Existing dependencies; no version pin is planned
```

**Structure Decision**: Keep the existing single-project layout and place the mode profile beside `OCREngine`. Rendering, recursive traversal, retry, resume parsing, and output assembly stay shared; a separate GLM engine or new configuration module would duplicate behavior without adding a distinct lifecycle.

## Complexity Tracking

No constitutional violations require justification.

## Post-Design Constitution Check

- **I. Quality-Driven Python Development — PASS**: The data model and contracts define typed values, validation boundaries, and unit/integration coverage for all new branches.
- **II. CLI-First Interface — PASS**: The CLI contract preserves both positional directory arguments and adds only optional, script-friendly flags.
- **III. Recursive Directory Processing — PASS**: The design explicitly leaves traversal, mirroring, page ordering, and resume parsing unchanged.
- **IV. Data Isolation — PASS**: The quickstart uses user-supplied paths; automated validation uses mocked API calls and temporary files.
- **V. Atomic Git Workflow — PASS**: The design remains confined to the identified OCR source, test, documentation, and feature-artifact files.

**Post-design gate result**: PASS. The Phase 1 design introduces no violations.
