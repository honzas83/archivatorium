# Tasks: DOCX Generation with Page Mirroring

**Input**: Design documents from `/specs/005-docx-generation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli.md

**Tests**: Included as per project standards and implementation plan.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Add `python-docx` to dependencies in `pyproject.toml`
- [x] T002 [P] Create the utility file `ocrpolish/utils/docx_utils.py`
- [x] T003 [P] Create integration test file `tests/integration/test_docx_generation.py`
- [x] T004 [P] Create unit test file `tests/unit/test_docx_utils.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Update `ocrpolish/data_model.py` to add `docx_enabled` to `ProcessingConfig`
- [x] T006 Update `ocrpolish/cli.py` to add the `--docx` command-line flag

**Checkpoint**: Foundation ready - CLI now accepts the flag and data models are updated.

---

## Phase 3: User Story 1 - Generate DOCX with Page Mirroring (Priority: P1) 🎯 MVP

**Goal**: Convert Markdown files to DOCX with page breaks mirroring original structure and using a fixed-width font.

**Independent Test**: Run `ocrpolish` on a test Markdown file with page markers using a mock flag, and verify the resulting DOCX has correct page counts and font.

### Tests for User Story 1

- [x] T007 [P] [US1] Write unit tests for page-splitting logic in `tests/unit/test_docx_utils.py`
- [x] T008 [P] [US1] Write unit tests for font styling logic in `tests/unit/test_docx_utils.py`

### Implementation for User Story 1

- [x] T009 [US1] Implement `split_markdown_by_pages` utility in `ocrpolish/utils/docx_utils.py`
- [x] T010 [US1] Implement `create_docx_from_pages` with `python-docx` in `ocrpolish/utils/docx_utils.py`
- [x] T011 [US1] Apply "Consolas" font styling to all paragraphs in `ocrpolish/utils/docx_utils.py`
- [x] T012 [US1] Integrate `docx_utils` into the `Processor` class in `ocrpolish/processor.py` to handle content conversion

**Checkpoint**: At this point, the system can generate a DOCX file from Markdown content with correct page breaks and fonts.

---

## Phase 4: User Story 2 - Optional DOCX Generation (Priority: P2)

**Goal**: Ensure DOCX generation only occurs when the `--docx` flag is explicitly provided.

**Independent Test**: Run `ocrpolish` without `--docx` and verify no DOCX is created; run with it and verify it is.

### Tests for User Story 2

- [x] T013 [P] [US2] Write integration test verifying DOCX file presence/absence based on flag in `tests/integration/test_docx_generation.py`

### Implementation for User Story 2

- [x] T014 [US2] Update `ocrpolish/core.py` to pass the `docx_enabled` setting to the processing loop
- [x] T015 [US2] Update `Processor.process_file` in `ocrpolish/processor.py` to conditionally call DOCX generation

**Checkpoint**: User stories 1 and 2 are complete and integrated.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T016 [P] Update `README.md` with DOCX generation usage instructions
- [x] T017 [P] Verify `quickstart.md` scenarios manually
- [x] T018 Run `ruff check .` and `ruff format .`
- [x] T019 Run `mypy .` to ensure type safety
- [x] T020 Run `pytest` and verify 100% success rate on new tests

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on T001.
- **User Stories (Phase 3+)**: Depend on Phase 2.
- **Polish (Final Phase)**: Depends on all user stories.

### Parallel Opportunities

- T002, T003, T004 (File creation)
- T007, T008 (US1 Unit tests)
- T013 (US2 Integration test)
- T016, T017 (Documentation/Validation)

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Complete Setup and Foundational phases.
2. Implement User Story 1 to prove core logic (MD -> DOCX conversion).
3. Verify with manual test.

### Incremental Delivery
1. Foundation -> Flag accepted but does nothing.
2. US1 -> Conversion logic works.
3. US2 -> Logic is correctly wired to the flag.
4. Polish -> Ready for production use.
