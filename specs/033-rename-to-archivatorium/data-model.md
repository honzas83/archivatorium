# Data Model & Architectural Entities: Rename to Archivatorium

This document describes the architectural entities, validation rules, and structural mappings for the transition from `ocrpolish` to `archivatorium`.

## 1. Mapped Entities

### Entity: Codebase Package
- **Source Path**: `ocrpolish/` (root directory)
- **Target Path**: `archivatorium/` (root directory)
- **Description**: The core Python package directory containing all source code modules, utility functions, and CLI definition.
- **Attributes**:
  - `name`: Target name is `archivatorium`.
  - `imports`: All Python file import statements matching `import ocrpolish` or `from ocrpolish ...` are updated to target `archivatorium`.
  - `casing`: Lowercase `ocrpolish` is replaced with `archivatorium`. Title-case/capitalized references are mapped to `Archivatorium`.

### Entity: CLI Entry Point
- **Old Command**: `ocrpolish`
- **New Command**: `archivatorium`
- **Configuration Path**: `pyproject.toml`
- **Attributes**:
  - `entry_point`: Mapped under `[project.scripts]` as `archivatorium = "archivatorium.cli:main"` (or the corresponding module name).
  - `package_name`: The package distribution name is changed to `archivatorium`.

### Entity: Spec Vault (Immutable)
- **Directory Path**: `specs/` (excluding the current directory `specs/033-rename-to-archivatorium/`)
- **Description**: Historical specification documents that must not be changed.
- **Validation Rules**:
  - No files under this folder should be edited during the rename process.
  - The tool configurations (`feature.json`, etc.) can point to subdirectories under `specs/` but files under prior features must be excluded from rename replacements.

## 2. Text Mapping Schema

The following case-sensitive translation rules must be validated during Phase 2 execution:

| Source Pattern | Target Pattern | Context |
|----------------|----------------|---------|
| `ocrpolish` | `archivatorium` | Python imports, package directory, CLI executable command name, lowercase descriptions |
| `OcrPolish` | `Archivatorium` | Title-case class names, descriptions |
| `OCR Polish` | `Archivatorium` | Natural language text, titles, README headers |
| `OCRPOLISH` | `ARCHIVATORIUM` | Environment variables, uppercase constants, configuration markers |
| `ocr_polish` | `archivatorium` | Python module or variable names |
