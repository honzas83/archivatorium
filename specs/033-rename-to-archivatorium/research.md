# Research & Technical Decisions: Rename Project to Archivatorium

This document outlines the design decisions and research findings for renaming the codebase, packages, commands, configurations, and documentations from `ocrpolish` to `archivatorium`.

## 1. Directory & Package Rename

- **Decision**: Rename the primary Python package directory from `ocrpolish/` to `archivatorium/`.
- **Rationale**: Keeps the Python import path (`import archivatorium`) fully consistent with the new project name, minimizing developer confusion.
- **Alternatives considered**: Keeping the package directory as `ocrpolish` but changing the CLI name (rejected, as import paths would mismatch the package distribution and command name, violating standard conventions).

## 2. Refactoring Tooling & Regex Replacements

- **Decision**: Perform a multi-cased regex-based search and replace across the codebase (excluding the `specs/` directory) to rename all instances. Specifically:
  - `ocrpolish` (lowercase) -> `archivatorium`
  - `OcrPolish` / `Ocrpolish` -> `Archivatorium`
  - `OCR Polish` (spaced) -> `Archivatorium`
  - `OCRPOLISH` (uppercase) -> `ARCHIVATORIUM`
- **Rationale**: Ensures complete consistency across code comments, module strings, configuration keys, and documentation.
- **Alternatives considered**: Manual find-and-replace (rejected as too error-prone due to the large number of occurrences).

## 3. Specification Vault Protection

- **Decision**: Configure all renaming scripts and text replacement commands to exclude the `specs/` directory (except for this feature folder `specs/033-rename-to-archivatorium/`).
- **Rationale**: Historical specification documents and execution plans represent historical milestones/snapshots and must be kept in their original state for audit integrity, as explicitly requested by the user.
- **Alternatives considered**: Renaming historical specs too (rejected, explicitly forbidden).

## 4. Package Configuration & Entry Points

- **Decision**: Update `pyproject.toml` to change `name` to `"archivatorium"` and update `[project.scripts]` to map `archivatorium = "archivatorium.cli:main"` (or equivalent entry point), and update the egg-info/build directories.
- **Rationale**: Aligns installation via `pip` / `uv` and CLI command availability with the new name.
- **Alternatives considered**: Keeping a fallback console script for `ocrpolish` (rejected to enforce complete transition to `archivatorium`).
