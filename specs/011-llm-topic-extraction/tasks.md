# Tasks: LLM Topic Extraction (Integrated)

**Input**: Design documents from `/specs/011-llm-topic-extraction/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create `ocrpolish/models/topics.py` for topic-related Pydantic schemas
- [x] T002 [P] Create `tests/test_topics_service.py` for unit testing the extraction logic
- [x] T003 Create `ocrpolish/services/topics_service.py` to house the extraction logic

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [x] T004 Define Pydantic schemas (`CategorySelectionSchema`, `TopicSelectionSchema`) in `ocrpolish/models/topics.py`
- [x] T005 [P] Implement YAML hierarchy loading logic in `ocrpolish/services/topics_service.py`
- [x] T006 Implement prompt template generation for categories in `ocrpolish/services/topics_service.py` (using 10kB raw text context)
- [x] T007 Implement prompt template generation for topics in `ocrpolish/services/topics_service.py` (with specific reasoning and limits)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Two-Step Topic Extraction (Priority: P1) 🎯 MVP

**Goal**: Implement the two-step LLM process using the raw document chunk to avoid metadata hallucinations.

**Independent Test**: Run a test script providing a text chunk, and verify that the two-step service returns correctly structured topic assignments (max 3) with reasoning.

### Implementation for User Story 1

- [x] T008 [US1] Implement category selection LLM call logic in `ocrpolish/services/topics_service.py`
- [x] T009 [US1] Implement topic selection LLM call logic (category-aware, max 3, mandatory reasoning) in `ocrpolish/services/topics_service.py`
- [x] T010 [US1] Implement combined `extract_topics` method in `ocrpolish/services/topics_service.py`
- [x] T011 [US1] Add unit tests for the two-step extraction flow in `tests/test_topics_service.py`

**Checkpoint**: Topic extraction logic is verified and ready for integration.

---

## Phase 4: User Story 2 - Obsidian Hierarchical Tagging (Priority: P1)

**Goal**: Format extracted topics into hierarchical Obsidian tags with hyphens and reasoning.

**Independent Test**: Verify that category "Cold War" and topic "Arms Control" results in `#Cold-War/Arms-Control — [Reason]`.

### Implementation for User Story 2

- [x] T012 [US2] Implement `format_hierarchical_tag` utility in `ocrpolish/utils/metadata.py`
- [x] T013 [P] [US2] Add unit tests for tag formatting and hyphenation in `tests/test_metadata_utils.py`
- [x] T014 [US2] Ensure tags are correctly formatted for list placement in the callout in `ocrpolish/processor_metadata.py`

**Checkpoint**: Tag formatting is verified.

---

## Phase 5: User Story 3 - Metadata Integration (Priority: P2)

**Goal**: Integrate the topic extraction service into the `metadata` command pass and rework callout layout.

**Independent Test**: Run `ocrpolish metadata` with `--hierarchy-file` and verify that tags appear exclusively in the Abstract callout sections.

### Implementation for User Story 3

- [x] T015 [US3] Update `MetadataProcessor.__init__` in `ocrpolish/processor_metadata.py` to accept an optional `TopicExtractor`
- [x] T016 [US3] Update `MetadataProcessor.process_file` in `ocrpolish/processor_metadata.py` to perform topic extraction and rework the callout to include `## Categories/Topics` and `## Tags` sections
- [x] T017 [US3] Add `--hierarchy-file` / `-h` option to the `metadata` command in `ocrpolish/cli.py`
- [x] T018 [US3] Wire the `TopicExtractor` into the `metadata` command logic in `ocrpolish/cli.py`

**Checkpoint**: Integration is complete and functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements and final validation

- [x] T019 [P] Update `README.md` with documentation for the new integrated topic extraction feature
- [x] T020 Run end-to-end integration tests (manual validation on sample documents)
- [x] T021 [P] Ensure all code passes quality checks (`ruff`, `mypy`, `pytest`)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: Completed.
- **Phase 2 (Foundational)**: Completed.
- **Phase 3 (US1)** and **Phase 4 (US2)**: Completed.
- **Phase 5 (US3)**: Completed.
- **Phase 6 (Polish)**: Completed.

### User Story Dependencies

- **US3 (Integration)**: Depends on US1 (Logic) and US2 (Formatting). Completed.

---

## Implementation Strategy

### MVP First (Full Integration)

All phases completed. The feature is fully integrated into the `metadata` command with the requested precision and formatting refinements.
