# Tasks: Precision Tagging System

**Input**: Design documents from `/specs/018-tagging-system/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are generated for each user story to ensure behavioral correctness.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Update `pyproject.toml` with new dependencies (`ollama`, `tiktoken`, `pydantic`)
- [x] T002 Initialize `ocrpolish/services/tagging_service.py` and `ocrpolish/services/windowing_service.py`
- [x] T003 [P] Configure quality tools for new structures in `.flake8` or `pyproject.toml`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Implement `WindowTaggingResult` and `AggregatedTaggingResult` models in `ocrpolish/models/metadata.py`
- [x] T005 [P] Implement `estimate_tokens(text: str) -> int` utility in `ocrpolish/utils/nlp.py`
- [x] T006 [P] Implement `SlidingWindowService` for document chunking in `ocrpolish/services/windowing_service.py`
- [x] T007 [P] Create `TaggingService` stub in `ocrpolish/services/tagging_service.py` with `think: false` configuration

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Multi-Output Tagging (Priority: P1) 🎯 MVP

**Goal**: Implement the two-pass architecture to extract Entities, Topics, and Conceptual tags.

**Independent Test**: Verify that a document processed in Step 2 pass produces three distinct tag lists in the output callout.

### Tests for User Story 1

- [x] T008 [P] [US1] Create integration test for two-pass tagging in `tests/integration/test_tagging_pass.py`
- [x] T009 [P] [US1] Create unit test for `TaggingService` dynamic pass logic in `tests/unit/test_tagging_service.py`

### Implementation for User Story 1

- [x] T010 [US1] Refactor `MetadataProcessor.process_file` in `ocrpolish/processor_metadata.py` to support Step 2 pass
- [x] T011 [US1] Implement `TaggingService.extract_tags` with dynamic Single-Pass/Sliding-Window logic in `ocrpolish/services/tagging_service.py`
- [x] T012 [US1] Implement Entity Tag extraction (`State/`, `Org/`, `City/`, `Person/`) in `TaggingService`
- [x] T013 [US1] Implement Topic Tag extraction (hierarchical taxonomy) in `TaggingService`
- [x] T014 [US1] Implement base Conceptual Tag extraction (flat tags) in `TaggingService`
- [x] T015 [US1] Update Obsidian callout generation to include "Mentioned Entities", "Categories/Topics", and "Tags" sections in `ocrpolish/processor_metadata.py`

**Checkpoint**: At this point, Multi-Output Tagging is functional and testable independently.

---

## Phase 4: User Story 2 - Tag Canonicalization and Noise Reduction (Priority: P1)

**Goal**: Filter noise, normalize exercises, and reuse tags from `USEFUL_TAGS.yaml`.

**Independent Test**: Verify that "Wintex-71" becomes `#WINTEX/71` and "agenda" is excluded from flat tags.

### Tests for User Story 2

- [x] T016 [P] [US2] Create unit tests for normalization rules in `tests/unit/test_nlp_normalization.py`
- [x] T017 [P] [US2] Create unit tests for canonical tag reuse in `tests/unit/test_tag_reuse.py`

### Implementation for User Story 2

- [x] T018 [P] [US2] Implement `normalize_exercise_tag` (e.g., `WINTEX/71`) in `ocrpolish/utils/nlp.py`
- [x] T019 [US2] Implement `filter_low_value_tags` (rejecting "report", "study", etc.) in `ocrpolish/utils/nlp.py`
- [x] T020 [US2] Integrate `USEFUL_TAGS.yaml` as primary reuse source in `TaggingService` prompt and refinement logic
- [x] T021 [US2] Apply TitleCase normalization and OCR error correction in `ocrpolish/utils/nlp.py`

**Checkpoint**: At this point, tags are clean, normalized, and consistent with the approved vocabulary.

---

## Phase 5: User Story 3 - Duplicate Suppression (Priority: P2)

**Goal**: Ensure conceptual tags do not duplicate information present in Entities or Topics.

**Independent Test**: Verify that if `Org/NATO` is present, `#NATO` is removed from the flat tags.

### Tests for User Story 3

- [x] T022 [P] [US3] Create unit tests for cross-tier duplicate suppression in `tests/unit/test_tag_suppression.py`

### Implementation for User Story 3

- [x] T023 [US3] Implement `suppress_duplicates(conceptual, entities, topics)` logic in `ocrpolish/utils/nlp.py`
- [x] T024 [US3] Integrate suppression logic into `TaggingService` aggregation step in `ocrpolish/services/tagging_service.py`

**Checkpoint**: All tag tiers are mutually exclusive and high-signal.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final refinements and verification.

- [x] T025 [P] Update `README.md` with the new two-pass tagging documentation
- [x] T026 Final code cleanup, type-hinting, and docstring verification across all new services
- [x] T027 Run full suite: `pytest --cov=ocrpolish tests/`
- [x] T028 Validate performance targets for 32k context and sliding window passes
- [x] T029 Run `quickstart.md` validation on sample NATO archive documents

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup.
- **User Stories (Phase 3-5)**: All depend on Foundational (Phase 2).
  - US1 (Phase 3) is the MVP and should be completed first.
  - US2 and US3 can proceed in parallel once US1 core logic is in place.
- **Polish (Phase 6)**: Depends on all user stories.

### User Story Dependencies

- **US1 (P1)**: Core functional increment.
- **US2 (P1)**: Enhances US1 with quality rules.
- **US3 (P2)**: Refines US1/US2 with suppression logic.

### Parallel Opportunities

- T005, T006, T007 can run in parallel within Phase 2.
- T008, T009 (tests) can run in parallel with T010-T014.
- T016, T017 can run in parallel with T018-T020.
- T022 can run in parallel with T023.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup and Foundational phases.
2. Implement US1: Two-pass tagging with raw Entity/Topic/Conceptual extraction.
3. Validate basic callout output.

### Incremental Delivery

1. Foundation ready.
2. US1 adds tiered tagging.
3. US2 adds canonicalization and noise filtering.
4. US3 adds strict cross-tier suppression.
