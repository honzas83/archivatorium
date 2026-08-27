# Implementation Plan: Add FireRed OCR Mode

**Branch**: `036-add-firered-mode` | **Date**: 2026-08-27 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/036-add-firered-mode/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add an opt-in `firered` OCR request profile. It sends the supplied FireRed Markdown-conversion prompt as the complete page instruction and never includes text recognized from another page. The implementation extends the established immutable OCR mode-profile mechanism, exposes the new choice through the existing OCR CLI option, and adds focused unit and integration regression coverage while preserving standard and GLM behavior.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: Click CLI, Ollama client, httpx, pdf2image, PyPDF2

**Storage**: Existing filesystem PDF-to-Markdown output; no schema or storage change

**Testing**: pytest, pytest-cov; ruff, flake8, and mypy quality gates

**Target Platform**: macOS and other supported CLI environments with PDF rendering and an Ollama-compatible OCR host

**Project Type**: CLI

**Performance Goals**: Retain existing per-page rendering, request, retry, and resume performance; the new profile adds no extra requests or page-text processing

**Constraints**: FireRed requests must use the exact supplied prompt and contain no recognized text from other pages; standard and GLM behavior must remain unchanged

**Scale/Scope**: One additional OCR mode across single-page, multipage, resumed, missing-page recovery, and retry flows

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Python 3.12 Development**: Pass. The existing Python CLI and its typed profile data model are extended without introducing another language or runtime.
- **CLI-First Interface**: Pass. The mode is exposed as one value of the existing `archivatorium ocr --mode` option.
- **Recursive Directory Processing**: Pass. Existing recursive input discovery and mirrored output handling are unchanged.
- **Data Isolation**: Pass. Tests use mocks and temporary directories; no PDF or model output will be added to version control.
- **Atomic Git Workflow**: Pass. Implementation tasks can be committed as focused profile/CLI, tests, and documentation changes without staging unrelated worktree changes.

*Pre-design status: **Passed***

## Project Structure

### Documentation (this feature)

```text
specs/036-add-firered-mode/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)
```text
archivatorium/
├── cli.py                         # OCR CLI mode choice and help
└── ocr_engine.py                  # OCR mode profiles and page requests

tests/
├── unit/
│   └── test_ocr_engine.py         # Profile, request, retry, and resume tests
└── integration/
    └── test_ocr_cli.py            # Public CLI selection and output tests
```

**Structure Decision**: Extend the existing monolithic CLI and OCR engine. A profile is the established abstraction for mode-specific request behavior, so no new service, storage layer, or command is needed.

## Complexity Tracking

No constitution violations or complexity exceptions are required.

## Post-Design Constitution Check

- **Quality-Driven Python Development**: Pass. The design assigns unit and integration coverage and retains all required linting, typing, and test gates.
- **CLI-First Interface**: Pass. The public contract is a documented addition to the current OCR CLI, with no alternate interface.
- **Recursive Directory Processing**: Pass. The profile is applied per page inside the existing recursive pipeline and does not change traversal or output mirroring.
- **Data Isolation**: Pass. The quickstart uses disposable paths; automated validation uses mocked clients and temporary files.
- **Atomic Git Workflow**: Pass. The source and focused tests are confined to the feature's OCR files and related documentation.

*Post-design status: **Passed***
