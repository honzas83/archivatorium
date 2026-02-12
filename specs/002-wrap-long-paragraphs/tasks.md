# Tasks: Inverted Paragraph Merging & Wrapping

**Input**: Design documents from `/specs/002-wrap-long-paragraphs/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `ocrpolish/`, `tests/` at repository root

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Verify environment installation (pip install ruff flake8 flake8-cognitive-complexity mypy pytest coverage)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [x] T002 Update unit test baseline in tests/unit/test_processor.py to reflect new wrapping expectations

---

## Phase 3: User Story 1 - Wrap Long Lines (Priority: P1) 🎯 MVP

**Goal**: Implement the core logic to wrap long lines while preserving short ones and protecting markdown structures.

**Independent Test**: Provide markdown files with long unwrapped paragraphs and verify they are word-wrapped at the typewriter width without merging unrelated lines.

### Implementation for User Story 1

- [x] T003 [P] [US1] Implement line-by-line wrapping logic using `textwrap` in ocrpolish/processor.py
- [x] T004 [US1] Remove line merging logic from `merge_paragraphs` (or rename to `wrap_lines`) in ocrpolish/processor.py
- [x] T005 [US1] Ensure all wrapped lines (after the first) are flush left in ocrpolish/processor.py
- [x] T006 [US1] Maintain protection for ANNEX, APPENDIX, and page numbers in ocrpolish/processor.py
- [x] T007 [P] [US1] Update unit tests for independent line wrapping in tests/unit/test_processor.py
- [x] T008 [US1] Update integration tests to verify no merging occurs between short lines in tests/integration/test_cleaning.py
- [x] T009 [US1] Update Pass 2 logic in ocrpolish/core.py to use the new wrapping function

**Checkpoint**: User Story 1 functional - long lines wrapped, short lines preserved.

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Improvements and final validation

- [x] T010 [P] Update documentation in README.md to reflect the "Wrap Only" strategy
- [x] T011 [P] Run all quality gates (ruff, flake8, mypy, pytest) across the codebase
- [x] T012 [P] Verify wrapping behavior against sample data in data/sample.txt

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup
- **User Story 1 (P1)**: Depends on Foundational

### Parallel Opportunities

- T003 and T007 can be started in parallel (implementation vs test preparation).
- T010 and T011 in the final phase can run together.
