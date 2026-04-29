# Tasks: LLM Flat Topic Extraction

**Input**: Design documents from `/specs/012-llm-flat-topic-extraction/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli.md

**Tests**: Included as per Constitution Principle I (Quality-Driven Development).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- File paths are project-relative.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Register `--flat-topics` flag in `ocrpolish/cli.py`
- [x] T002 [P] Create empty `ocrpolish/services/flattening_service.py` for linearization logic

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [x] T003 Update `ocrpolish/models/topics.py` with `FlatTopicAssignment` and `FlatTopicSelectionSchema` models

---

## Phase 3: User Story 2 - Hierarchy Flattening (Priority: P2)

**Goal**: Transform nested Category/Topic structure into a flat list format with path-like IDs.

**Independent Test**: Provide a nested YAML hierarchy and verify the output is a correctly formatted flat YAML list with all samples.

### Tests for User Story 2

- [x] T004 [P] [US2] Unit test for flattening logic in `tests/unit/test_flattening.py`

### Implementation for User Story 2

- [x] T005 [US2] Implement `FlatteningService.flatten()` in `ocrpolish/services/flattening_service.py` to produce "Category/Topic" IDs
- [x] T006 [US2] Implement sample extraction logic in `ocrpolish/services/flattening_service.py`

**Checkpoint**: Hierarchy flattening is functional and can be tested independently of the LLM.

---

## Phase 4: User Story 1 - Single-step classification (Priority: P1) 🎯 MVP

**Goal**: Identify topics in a single LLM call using the flat hierarchy and samples.

**Independent Test**: Provide a document and a flat hierarchy, verify LLM returns assignments that map correctly to original categories.

### Tests for User Story 1

- [x] T007 [P] [US1] Integration test for flat extraction in `tests/integration/test_flat_extraction.py`
- [x] T008 [P] [US1] Unit test for prompt construction in `tests/unit/test_topics_service_flat.py`

### Implementation for User Story 1

- [x] T009 [US1] Update `TopicExtractor` in `ocrpolish/services/topics_service.py` to support flat mode
- [x] T010 [US1] Implement `_generate_flat_topic_prompt()` in `ocrpolish/services/topics_service.py` using YAML format
- [x] T011 [US1] Implement `extract_topics_flat()` in `ocrpolish/services/topics_service.py` with Pydantic mapping
- [x] T012 [US1] Connect CLI flags to `TopicExtractor` in `ocrpolish/cli.py` and `ocrpolish/processor_metadata.py`

**Checkpoint**: MVP is ready. Topic extraction can now use the single-pass flat method.

---

## Phase 5: User Story 3 - Accuracy Comparison (Priority: P3)

**Goal**: Quantify accuracy improvement of flat vs. multi-step classification.

**Independent Test**: Run evaluation script and verify it reports F1 scores for both methods.

### Implementation for User Story 3

- [x] T013 [P] [US3] Create evaluation utility in `tests/evaluate_topic_accuracy.py` to compare methods on gold-standard data

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation and cleanup.

- [x] T014 [P] Update `docs/LLM_METADATA_EXTRACTION.md` with flat extraction documentation
- [x] T015 Run `quickstart.md` validation and final quality checks (ruff, mypy)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Phase 1.
- **US2 (Phase 3)**: Depends on Phase 2. *Note: US1 depends on US2 logic.*
- **US1 (Phase 4)**: Depends on US2 completion.
- **US3 (Phase 5)**: Depends on US1 and US2 completion.

### Parallel Opportunities

- T002 (Setup) can run in parallel with T001.
- T004 (US2 Tests) can be drafted while T003 (Models) is in progress.
- T007 and T008 (US1 Tests) can be written before US1 implementation.
- T013 (Evaluation) can be drafted while US1 is in progress.

---

## Implementation Strategy

### MVP First (User Story 1 & 2)

1. Complete Setup and Foundational.
2. Complete US2 (Flattening) as it is the engine for US1.
3. Complete US1 (Classification) to deliver the core value.
4. **STOP and VALIDATE**: Run integration tests to confirm accuracy improvement.

### Incremental Delivery

1. Setup + Models → Foundation ready.
2. Flattening Service → Test with various hierarchies.
3. Single-pass Extraction → Full MVP ready.
4. Comparison Utility → Validation of improvement.
