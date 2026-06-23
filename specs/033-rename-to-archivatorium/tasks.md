# Tasks: Rename Project to Archivatorium

**Input**: Design documents from `/specs/033-rename-to-archivatorium/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure verification before rename

- [x] T001 Run initial sanity check of test suite and CLI execution with old name using `pytest` and command `ocrpolish --help`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core package directory and configuration rename which must be complete before any user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T002 Rename core source folder from `ocrpolish/` to `archivatorium/`
- [x] T003 Update packaging configuration, metadata, and console script entry point in `pyproject.toml`
- [x] T004 [P] Update module path reference and pythonpath settings in `tests/conftest.py`
- [x] T005 [P] Update all imports from ocrpolish to archivatorium in files under `tests/`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Run the Command Line Interface (Priority: P1) 🎯 MVP

**Goal**: Users can run the CLI via the new `archivatorium` command and access all subcommands

**Independent Test**: Install the package, run `archivatorium --help` and verify subcommands list successfully

### Implementation for User Story 1

- [x] T006 [US1] Update imports and references to archivatorium inside `archivatorium/cli.py`
- [x] T007 [US1] Reinstall package and test command-line invocation of `archivatorium --help` using `pyproject.toml`
- [x] T008 [US1] Add CLI invocation integration test in `tests/test_cli.py`

**Checkpoint**: At this point, User Story 1 is fully functional and testable independently

---

## Phase 4: User Story 2 - Python Package Imports and Code References (Priority: P2)

**Goal**: Renaming of all internal import paths and module variable names across the codebase

**Independent Test**: All unit and integration tests under `tests/` import and run from the renamed package successfully

### Implementation for User Story 2

- [x] T009 [P] [US2] Update imports and references in core modules `archivatorium/core.py` and `archivatorium/data_model.py`
- [x] T010 [P] [US2] Update imports and references in engine modules `archivatorium/ocr_engine.py` and `archivatorium/processor_metadata.py`
- [x] T011 [P] [US2] Update imports and references in services files under `archivatorium/services/`
- [x] T012 [P] [US2] Update imports and references in utilities files under `archivatorium/utils/`
- [x] T013 [US2] Run pytest to verify all tests pass under the new archivatorium module in `tests/`

**Checkpoint**: At this point, User Stories 1 and 2 work independently and all codebase modules are fully updated

---

## Phase 5: User Story 3 - Documentation and Configuration Renaming (Priority: P3)

**Goal**: Rename all occurrences of ocrpolish / OCR Polish in docs and settings files (skipping specs/)

**Independent Test**: Text search for case-insensitive `ocrpolish` yields no results outside `specs/` and `.git/`

### Implementation for User Story 3

- [x] T014 [P] [US3] Update documentation file `README.md` with the new project name
- [x] T015 [P] [US3] Update documentation/context files `GEMINI.md` and `AGENTS.md` with the new project name
- [x] T016 [P] [US3] Update specification configuration files under `.specify/`
- [x] T017 [P] [US3] Update environment/tool configuration files `.envrc` and `.gitignore`

**Checkpoint**: All documentation and configurations are updated

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T018 Run global case-insensitive search to confirm no active ocrpolish references exist outside `specs/`
- [x] T019 Run quickstart.md validation steps in `specs/033-rename-to-archivatorium/quickstart.md` to ensure clean setup and execution

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3 to 5)**: All depend on Foundational phase completion
  - User Story 1 (P1) is the MVP and should be completed first
  - User Story 2 (P2) depends on code structure but can run in parallel with US1 CLI imports cleanup
  - User Story 3 (P3) can run independently after Foundation is complete
- **Polish (Phase 6)**: Depends on all user stories being complete

### Parallel Opportunities

- Foundational tasks `T004` and `T005` can run in parallel
- Once Foundational phase is complete:
  - Developer A: User Story 1 (T006, T007, T008)
  - Developer B: User Story 2 (T009, T010, T011, T012, T013)
  - Developer C: User Story 3 (T014, T015, T016, T017)
- Tasks `T009`, `T010`, `T011`, and `T012` within US2 can run in parallel
- Tasks `T014`, `T015`, `T016`, and `T017` within US3 can run in parallel

---

## Parallel Example: User Story 2 & 3

```bash
# Launch parallel edits on core, engine, service, and utility files:
Task: "Update imports and references in core modules"
Task: "Update imports and references in engine modules"
Task: "Update imports and references in services"
Task: "Update imports and references in utilities"

# Launch parallel documentation and config updates:
Task: "Update documentation file README.md with the new project name"
Task: "Update documentation/context files GEMINI.md and AGENTS.md"
Task: "Update specification configuration files under .specify/"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (Verify baseline works)
2. Complete Phase 2: Foundational (Rename directories and config files)
3. Complete Phase 3: User Story 1 (Restore CLI operation)
4. **STOP and VALIDATE**: Verify CLI functions under the new name `archivatorium`

### Incremental Delivery

1. Foundation: Directory rename + configs updated
2. MVP CLI: Restore `archivatorium` command operation
3. Code Cleanliness: Refactor all import paths inside codebase
4. Identity: Rename documentation and configurations (excluding specs/)
5. Validation: Run end-to-end check
