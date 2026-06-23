# Feature Specification: Rename Project to Archivatorium

**Feature Branch**: `033-rename-to-archivatorium`

**Created**: 2026-06-23

**Status**: Draft

**Input**: User description: "In this specification, we will rename the OCR Polish to Archivatorium, rename all code, documentations commands and other references, do not touch the existing specs/ . If the all-lower-case name ocrpolish was used, use archivatorium."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run the Command Line Interface (Priority: P1)

Users of the command-line interface need to execute the post-processing and tagging pipeline using the new name. The old CLI command `ocrpolish` should be replaced by `archivatorium` without loss of functionality.

**Why this priority**: High priority as the CLI is the primary user-facing interface for the tool, as defined by Core Principle II (CLI-First).

**Independent Test**: Install the renamed package and run the new CLI commands (e.g. `archivatorium clean`, `archivatorium metadata`) on sample inputs, confirming they execute successfully, and that the old `ocrpolish` command is no longer registered or used.

**Acceptance Scenarios**:

1. **Given** the package is installed in the active Python environment, **When** the user runs `archivatorium --help`, **Then** the help page for the CLI tool is displayed, showing the project description with the new name.
2. **Given** the package is installed, **When** the user runs `ocrpolish --help`, **Then** the shell returns a command-not-found or similar error (or deprecation notice, but complete removal is expected).

---

### User Story 2 - Python Package Imports and Code References (Priority: P2)

Developers and tools importing the package or using its internal APIs must import from the `archivatorium` module instead of `ocrpolish`.

**Why this priority**: Important for developers working on the codebase, ensuring that the code itself matches the project name.

**Independent Test**: Verify that the main source directory is renamed from `ocrpolish/` to `archivatorium/`, all `import ocrpolish` statements in the code and tests are changed to `import archivatorium`, and `pytest` runs and passes all unit and integration tests.

**Acceptance Scenarios**:

1. **Given** the source directory has been renamed to `archivatorium/`, **When** the test suite is run with `pytest`, **Then** all tests discover and import from the new module and pass without errors.
2. **Given** a python script outside the package, **When** it tries to `import ocrpolish`, **Then** it fails with `ModuleNotFoundError`, and **When** it tries to `import archivatorium`, **Then** it succeeds.

---

### User Story 3 - Documentation and Configuration Renaming (Priority: P3)

Users and developers reading documentation or inspecting configuration files (like `README.md`, `pyproject.toml`, `AGENTS.md`, `GEMINI.md`, etc., excluding `specs/` directory) see the name "Archivatorium" (or "archivatorium") instead of "OCR Polish" (or "ocrpolish").

**Why this priority**: Low priority compared to functional CLI and import changes, but crucial for project identity and consistency.

**Independent Test**: Perform a text search across all non-spec files in the project to verify that no instances of `ocrpolish` or `OCR Polish` (case-insensitive) remain in active documentation or configuration.

**Acceptance Scenarios**:

1. **Given** all project documents are updated, **When** inspecting `pyproject.toml` or `README.md`, **Then** references to `ocrpolish` are replaced with `archivatorium`.
2. **Given** the specs directory contains historical specs, **When** performing a text search under `specs/`, **Then** references to `ocrpolish` remain unmodified.

---

### Edge Cases

- **Casing Variations**: The codebase and documentation may contain multiple casings (e.g., `ocrpolish`, `OcrPolish`, `OCR Polish`, `OCR-Polish`, `OCRPOLISH`). The system must map:
  - `ocrpolish` -> `archivatorium`
  - `OCR Polish` -> `Archivatorium`
  - `OcrPolish` -> `Archivatorium`
  - `ocr-polish` -> `archivatorium`
- **Specification Directory Preservation**: Historical specifications in the `specs/` directory must NOT be modified. This must be strictly checked during renaming scripts or search-and-replace actions to prevent altering audit trails.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The root source directory `ocrpolish/` MUST be renamed to `archivatorium/`.
- **FR-002**: All Python files, configuration files, and tests MUST use `import archivatorium` or submodules thereof, and all references to the old module `ocrpolish` MUST be removed.
- **FR-003**: The distribution name, CLI console script entry point, and metadata in `pyproject.toml` MUST be renamed to `archivatorium`.
- **FR-004**: The command-line entry point MUST be updated so that the user executes the tool via `archivatorium [args]` instead of `ocrpolish [args]`.
- **FR-005**: All configuration files at the root of the repository, including `AGENTS.md`, `GEMINI.md`, `.envrc`, and any files under `.specify/` (e.g. `extensions.yml`, `init-options.json`), MUST be updated to rename project/command references, EXCEPT for the contents of the `specs/` directory.
- **FR-006**: Existing specification files and plans located under the `specs/` directory MUST remain untouched and unmodified.
- **FR-007**: Development tools configuration (e.g., `.gitignore`, `.ruff_cache`, `.pytest_cache`, and active IDE settings if stored in workspace) MUST be updated to reflect the new module/command name where necessary.

### Key Entities

- **Archivatorium Package**: Represents the renamed Python codebase, containing all core logic, utilities, and commands.
- **Archivatorium CLI**: The user-facing command-line tool, mapping arguments to core package functions under the new name.
- **Historical Specs Vault**: The directory `specs/` containing immutable feature requirements and implementation details of past features, which must be skipped during the renaming process.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of functional codebase, tests, and configuration files (excluding `specs/`) are free of the terms `ocrpolish` and `OCR Polish` (case-insensitive).
- **SC-002**: Running the command `archivatorium` performs the exact same operations as the former `ocrpolish` command.
- **SC-003**: The entire test suite (`pytest`) runs and passes on the renamed package.
- **SC-004**: Code quality checks (`ruff check .`, `mypy .`) pass without errors after renaming.
- **SC-005**: The `specs/` directory contents remain completely identical to their state prior to the rename.

## Assumptions

- Renaming of the physical project workspace directory (`/Users/honzas/Research.local/ocrpolish`) on the host system is out of scope for this task and may be handled by the user/host environment separately.
- Git commit history does not need to be rewritten to rename references in old commits.
- Git repository remotes and tracking remain unchanged, except for branch naming conventions if specified.
