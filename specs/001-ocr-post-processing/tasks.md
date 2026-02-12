# Tasks: OCR Post-Processing

**Input**: Design documents from `/specs/001-ocr-post-processing/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `ocrpolish/`, `tests/` at repository root
- Paths shown below assume single project - adjust based on plan.md structure

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project structure per implementation plan (ocrpolish/, tests/, tests/unit/, tests/integration/, data/)
- [x] T002 Initialize Python project with environment installation (pip install ruff flake8 flake8-cognitive-complexity mypy pytest coverage)
- [x] T003 [P] Configure quality tools (pyproject.toml or setup.cfg) for ruff, mypy, and pytest

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Implement basic directory scanning utility in ocrpolish/utils/files.py
- [x] T005 [P] Implement CLI argument parsing using argparse in ocrpolish/cli.py
- [x] T006 [P] Create base ProcessingConfig entity in ocrpolish/data_model.py
- [x] T007 Setup logging infrastructure in ocrpolish/utils/logging.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 2 - Preserve Directory Structure (Priority: P2)

**Goal**: Enable recursive processing and directory mirroring to maintain organization

**Independent Test**: Provide a nested input directory and verify the output directory has the same hierarchy and files (even if content is not yet cleaned)

### Implementation for User Story 2

- [x] T008 [P] [US2] Implement recursive directory walk and input mask filtering in ocrpolish/utils/files.py
- [x] T009 [US2] Implement directory mirroring logic (mkdir -p) in ocrpolish/utils/files.py
- [x] T010 [US2] Create integration test for directory structure replication in tests/integration/test_cli.py
- [x] T011 [US2] Wire CLI to use the mirroring logic in ocrpolish/cli.py

**Checkpoint**: At this point, User Story 2 should be functional - files are moved to mirrored structure

---

## Phase 4: User Story 1 - Clean OCR Text (Priority: P1) 🎯 MVP

**Goal**: Implement the core 2-pass cleaning logic (statistical headers/footers and paragraph merging)

**Independent Test**: Provide markdown files with known repeating headers and broken paragraphs and verify the output is clean

### Implementation for User Story 1

- [x] T012 [P] [US1] Implement Pass 1: GlobalFrequencyMap and line counting in ocrpolish/core.py
- [x] T013 [P] [US1] Implement Pass 2: Header/Footer removal logic in ocrpolish/processor.py
- [x] T014 [US1] Add page numbering protection (FR-003a) to header/footer removal in ocrpolish/processor.py
- [x] T015 [P] [US1] Implement Paragraph Merging logic with markdown protection (FR-005) in ocrpolish/processor.py
- [x] T016 [US1] Implement empty line paragraph spacing (FR-006) in ocrpolish/processor.py
- [x] T017 [US1] Create unit tests for cleaning logic in tests/unit/test_processor.py
- [x] T018 [US1] Create integration test for full cleaning flow in tests/integration/test_cli.py
- [x] T019 [US1] Integrate 2-pass logic into main execution flow in ocrpolish/core.py

**Checkpoint**: At this point, User Story 1 should be fully functional - core value delivered

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements and final validation

- [x] T020 [P] Finalize documentation and usage examples in README.md
- [x] T021 [P] Run all quality gates (ruff, flake8, mypy, pytest) across the codebase
- [x] T022 [P] Verify SC-001 through SC-005 against sample data in data/sample.txt
- [x] T023 Final code cleanup and refactoring for performance

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup
- **User Story 2 (P2)**: Depends on Foundational. Chosen to be implemented early because mirroring is simpler than cleaning.
- **User Story 1 (P1)**: Depends on Foundational. Can run in parallel with US2 if files are distinct, but depends on core structure.

### Implementation Strategy

- **MVP**: The combination of Phase 1, 2, and 4 constitutes the MVP. Phase 3 (Mirroring) is highly recommended for any real-world OCR batch.
- **Incremental Delivery**:
  1. Setup + Foundation
  2. Recursive Mirroring (Files moved correctly)
  3. Cleaning Logic (Content cleaned correctly)
  4. Final Polish

## Parallel Opportunities

- T005 and T006 can run in parallel (different files)
- T012, T013, and T015 can be developed in parallel as they focus on different parts of the processing logic
- All quality gate tasks in the final phase can run in parallel
