# Tasks: Metadata Citations

**Input**: Design documents from `specs/016-metadata-citations/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Tests are requested via independent test criteria in `spec.md`.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Verify project structure and configuration per implementation plan
- [x] T002 Update `GEMINI.md` with new feature context (Done in plan phase)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core utilities that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 [P] Create citation formatting utility in `ocrpolish/utils/metadata.py` (empty stubs)
- [x] T004 [P] Create unit test file `tests/unit/test_citations.py` with failing tests for basic formatting
- [x] T005 [P] Create integration test file `tests/integration/test_metadata_citations.py` to verify callout generation

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Standard Citation Generation (Priority: P1) 🎯 MVP

**Goal**: Generate standardized Chicago, Harvard, and BibTeX citations in an Obsidian callout.

**Independent Test**: Generate a document and verify the `> [!citing this document]` callout contains all three styles.

### Tests for User Story 1

- [x] T006 [P] [US1] Implement unit tests in `tests/unit/test_citations.py` for Chicago style formatting
- [x] T007 [P] [US1] Implement unit tests in `tests/unit/test_citations.py` for Harvard style formatting
- [x] T008 [P] [US1] Implement unit tests in `tests/unit/test_citations.py` for BibTeX style formatting
- [x] T009 [US1] Implement integration test in `tests/integration/test_metadata_citations.py` for full callout inclusion

### Implementation for User Story 1

- [x] T010 [US1] Implement `format_chicago_citation` in `ocrpolish/utils/metadata.py`
- [x] T011 [US1] Implement `format_harvard_citation` in `ocrpolish/utils/metadata.py`
- [x] T012 [US1] Implement `format_bibtex_citation` in `ocrpolish/utils/metadata.py`
- [x] T013 [US1] Implement `generate_citation_callout` helper in `ocrpolish/utils/metadata.py` combining all styles
- [x] T014 [US1] Update `MetadataProcessor.process_file` in `ocrpolish/processor_metadata.py` to append the citation callout at the end of the file
- [x] T015 [US1] Add logic to `MetadataProcessor` to handle `URLDate` (today's date)

**Checkpoint**: User Story 1 is functional and verifiable.

---

## Phase 4: User Story 2 - Default Platform and URL Placeholders (Priority: P2)

**Goal**: Use default values for platform name and handle URL placeholders correctly.

**Independent Test**: Verify citations use "NATO Archive Obsidian" and the specific `nato-obsidian.kky.zcu.cz` URL.

### Tests for User Story 2

- [x] T016 [P] [US2] Add unit tests in `tests/unit/test_citations.py` for default platform name handling
- [x] T017 [P] [US2] Add unit tests in `tests/unit/test_citations.py` for ArchiveCode-based URL placeholder

### Implementation for User Story 2

- [x] T018 [US2] Update `format_chicago_citation` and others to use default platform name "NATO Archive Obsidian" if not provided
- [x] T019 [US2] Implement ArchiveCode-based URL generation in `ocrpolish/utils/metadata.py`
- [x] T020 [US2] Ensure `MetadataProcessor` passes correct parameters for URL generation

**Checkpoint**: User Story 2 is functional and verifiable.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements and final validation

- [x] T021 [P] Run `ruff check .` and `ruff format .` to ensure code style
- [x] T022 [P] Run `mypy .` to verify type hints
- [x] T023 Run `coverage run -m pytest` and verify 100% coverage on new code
- [x] T024 Perform manual validation using `quickstart.md` examples

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Setup. Blocks implementation.
- **User Stories (Phase 3+)**: Depend on Foundational completion.
- **Polish (Final Phase)**: Depends on all user stories.

### Parallel Opportunities

- T003, T004, T005 (Foundational) can be created in parallel.
- Unit tests for different styles (T006, T007, T008) can be written in parallel.
- Formatting functions (T010, T011, T012) can be implemented in parallel.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Foundational phase.
2. Complete User Story 1 (P1).
3. **VALIDATE**: Run integration tests to confirm citations appear in generated MD.

### Incremental Delivery

1. Add User Story 2 refinements.
2. Final polish and style checks.
