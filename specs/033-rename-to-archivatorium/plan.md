# Implementation Plan: Rename Project to Archivatorium

**Branch**: `033-rename-to-archivatorium` | **Date**: 2026-06-23 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/033-rename-to-archivatorium/spec.md`

## Summary

The goal of this feature is to rename the toolkit from `ocrpolish` to `archivatorium`. This involves renaming the core Python package directory, updating all code imports, renaming CLI executable command scripts in `pyproject.toml`, and updating documentation and configuration files, while strictly preserving the integrity and contents of the existing historical feature directories in `specs/`.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: `click`, `PyYAML`, `python-docx`, `xlsxwriter`, `ollama` (configured in `pyproject.toml`)

**Storage**: Local Filesystem input/output directory mirroring

**Testing**: `pytest` / `pytest-cov`

**Target Platform**: macOS, standard POSIX shells

**Project Type**: CLI tool and Python package

**Performance Goals**: N/A (Rename migration should not introduce runtime overhead or affect performance).

**Constraints**:
- Existing specification directories (e.g. `specs/001-*` through `specs/032-*`) must NOT be modified.
- Casing mappings must be respected:
  - `ocrpolish` (lowercase) -> `archivatorium`
  - `OcrPolish` / `Ocrpolish` -> `Archivatorium`
  - `OCR Polish` -> `Archivatorium`
  - `OCRPOLISH` -> `ARCHIVATORIUM`
  - `ocr_polish` -> `archivatorium`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Gate 1: CLI-First Interface**: Mapped executable command script in `pyproject.toml` is renamed to `archivatorium`. (Pass)
- **Gate 2: Quality-Driven Python Development**: Keeps using Python 3.12, strict type hints, and quality tools (`ruff`, `mypy`, `pytest`). (Pass)
- **Gate 3: Recursive Directory Processing**: Preservation of recursive filesystem output logic. (Pass)
- **Gate 4: Data Isolation**: No new large datasets are added to the codebase. (Pass)
- **Gate 5: Atomic Git Workflow**: Renaming tasks are split cleanly and commits will only contain relevant modified files. (Pass)

**Status**: All Gates Pass. No violations.

## Project Structure

### Documentation (this feature)

```text
specs/033-rename-to-archivatorium/
├── plan.md              # This file
├── research.md          # Refactoring decisions
├── data-model.md        # Architectural entities definition
├── quickstart.md        # Verification and validation scenarios
└── checklists/
    └── requirements.md  # Quality gate requirements checklist
```

### Source Code (repository root)

```text
archivatorium/           # Renamed from ocrpolish/
├── __init__.py
├── cli.py
├── core.py
├── data_model.py
├── ocr_engine.py
├── processor_metadata.py
├── services/
│   ├── indexing_service.py
│   ├── interlinking_service.py
│   ├── ollama_client.py
│   ├── tagging_service.py
│   └── windowing_service.py
├── utils/
│   ├── files.py
│   ├── logging.py
│   └── metadata.py
tests/
├── conftest.py
├── test_cli.py
├── test_core.py
├── test_docx_utils.py
├── test_indexing.py
├── test_interlinking.py
├── test_metadata.py
├── test_ocr.py
├── test_tagging.py
└── test_windowing.py
```

**Structure Decision**: Single project layout with the main package renamed from `ocrpolish` to `archivatorium` and tests adjusted accordingly.

## Complexity Tracking

No violations found. Section not applicable.
