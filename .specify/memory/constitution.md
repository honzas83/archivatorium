<!--
Sync Impact Report:
- Version change: Initial -> 1.0.0
- List of modified principles:
  - Added: I. Quality-Driven Python Development
  - Added: II. CLI-First Interface
  - Added: III. Recursive Directory Processing
  - Added: IV. Data Isolation
  - Added: V. Atomic Git Workflow
- Added sections: Tooling & Quality Gates, Project Structure
- Removed sections: None
- Templates requiring updates:
  - .specify/templates/plan-template.md (✅ updated)
  - .specify/templates/tasks-template.md (✅ updated)
- Follow-up TODOs: None
-->

# ocrpolish Constitution

## Core Principles

### I. Quality-Driven Python Development
Development MUST be performed in Python. High code quality is non-negotiable and MUST be enforced using `ruff` for linting/formatting, `flake8` with cognitive complexity checks, and `mypy` for static type checking. Testing MUST use `pytest` with `coverage` reporting to ensure robust functionality.

### II. CLI-First Interface
The primary interface for `ocrpolish` MUST be a Command Line Interface (CLI). It MUST be designed for ease of use in both interactive sessions and automated pipelines, following standard POSIX-style argument patterns.

### III. Recursive Directory Processing
The tool MUST support recursive processing of directories. It MUST search for markdown (`*.md`) files in a specified input directory and replicate the directory structure in the output directory, ensuring that the original context is preserved.

### IV. Data Isolation
All sample, test, and real-world data MUST reside in a `data/` directory at the project root. This directory MUST be excluded from version control via `.gitignore` to prevent leaking sensitive information or bloating the repository with binary/large text blobs.

### V. Atomic Git Workflow
Developers MUST commit changes in small, logical increments. Every completed task from the implementation plan MUST result in a stable commit. This ensures a clean history and simplifies debugging and rollbacks.

## Tooling & Quality Gates
To maintain the standards set in Principle I, the following tools MUST be configured and pass before any feature is considered complete:
- **Linting**: `ruff check .`
- **Formatting**: `ruff format .`
- **Complexity**: `flake8` with `flake8-cognitive-complexity`.
- **Typing**: `mypy .`
- **Testing**: `pytest`
- **Coverage**: `coverage run -m pytest` and `coverage report`.

## Project Structure
The repository MUST follow this structure:
- `ocrpolish/`: Core source code.
- `tests/`: Test suite mirroring source structure.
- `data/`: Local data (gitignored).
- `specs/`: Feature specifications and plans.

## Governance
This constitution is the supreme authority on project standards for `ocrpolish`. Amendments MUST be made via the `speckit.constitution` process and require a version bump. All PRs and automated checks MUST verify compliance with these principles.

**Version**: 1.0.0 | **Ratified**: 2026-02-12 | **Last Amended**: 2026-02-12
