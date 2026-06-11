# Tasks: Fix Tag and Interlink Bugs

**Input**: Design documents from `specs/029-fix-tag-interlinks/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Test tasks are included because the feature specification and quickstart define independent validation for each story.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story the task belongs to
- Each task includes exact file paths

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish the implementation baseline and confirm the affected files before changing behavior.

- [X] T001 Review current parser, interlink, and tagging code paths in `ocrpolish/utils/tag_parser.py`, `ocrpolish/services/interlinking_service.py`, `ocrpolish/models/metadata.py`, `ocrpolish/services/tagging_service.py`, and `ocrpolish/processor_metadata.py`
- [X] T002 [P] Review existing parser and interlink regression tests in `tests/unit/test_tag_parser.py`, `tests/unit/test_interlinking_service.py`, and `tests/integration/test_interlink_cli.py`
- [X] T003 [P] Review existing topic counter and tagging tests in `tests/unit/test_processor_counters.py`, `tests/unit/test_tagging_service.py`, and `tests/integration/test_tagging_pass.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add shared fixtures and test setup needed by multiple stories.

**CRITICAL**: No user story work should begin until these shared fixtures are ready.

- [X] T004 [P] Add reusable tag parser examples for slash-containing org/state tags in `tests/unit/test_tag_parser.py`
- [X] T005 [P] Add reusable nested document target path fixtures for language-version, references-row, and body-link cases in `tests/unit/test_interlinking_service.py`
- [X] T006 [P] Add reusable topic counter population helper for more than 100 topic entries in `tests/unit/test_processor_counters.py`
- [X] T007 [P] Add reusable dense taxonomy/topic response fixture in `tests/unit/test_tagging_service.py`

**Checkpoint**: Shared fixtures are available for story tests.

---

## Phase 3: User Story 1 - Keep Generated Entity Tags Valid (Priority: P1) MVP

**Goal**: Generated organization and state tags with slashes in their names are normalized to dash-separated names and accepted without false malformed-tag warnings.

**Independent Test**: Parse text containing `#Entities/Org/OTAN/NATO`, `#Entities/Org/NAC/DP`, `#Entities/Org/Council/DPC`, and `#Entities/State/USA/California`; verify accepted raw paths, entity collections, and no malformed warning for those examples.

### Tests for User Story 1

- [X] T008 [P] [US1] Add parser contract tests for slash-containing organization and state examples in `tests/unit/test_tag_parser.py`
- [X] T009 [P] [US1] Add warning-capture regression test for slash-containing organization and state examples in `tests/unit/test_tag_parser.py`
- [X] T010 [P] [US1] Add regression test proving malformed non-slash organization/state tags still warn in `tests/unit/test_tag_validation.py`

### Implementation for User Story 1

- [X] T011 [US1] Implement slash-to-dash normalization for generated organization and state entity names before fixed-shape validation in `ocrpolish/utils/tag_parser.py`
- [X] T012 [US1] Preserve existing city, topic, conceptual tag, unsupported entity, and empty-component validation behavior in `ocrpolish/utils/tag_parser.py`
- [X] T013 [US1] Run `pytest tests/unit/test_tag_parser.py tests/unit/test_tag_validation.py` and fix regressions in `ocrpolish/utils/tag_parser.py` or affected tests

**Checkpoint**: User Story 1 is independently functional and testable.

---

## Phase 4: User Story 2 - Use Portable Interlinks Between Documents (Priority: P2)

**Goal**: All generated document-to-document interlinks use only the target filename while preserving labels, self-link prevention, idempotency, and unrelated non-generated links.

**Independent Test**: Generate interlinks for documents with nested target paths and verify language-version, references-row, and body links point to filenames such as `NPG-D(74)12_FRE.md` or `NPG(STUDY)38_ENG.md` rather than parent-folder paths.

### Tests for User Story 2

- [X] T014 [P] [US2] Add unit test for filename-only language-version links from nested stored paths in `tests/unit/test_interlinking_service.py`
- [X] T015 [P] [US2] Add unit test proving filename punctuation is preserved in generated document links in `tests/unit/test_interlinking_service.py`
- [X] T016 [P] [US2] Add unit test for filename-only references-row links from nested stored paths in `tests/unit/test_interlinking_service.py`
- [X] T017 [P] [US2] Add unit test for filename-only body links from nested stored paths in `tests/unit/test_interlinking_service.py`
- [X] T018 [P] [US2] Add CLI integration regression for nested language-version links in `tests/integration/test_interlink_cli.py`
- [X] T019 [P] [US2] Add CLI integration regression for nested references-row and body links in `tests/integration/test_interlink_cli.py`

### Implementation for User Story 2

- [X] T020 [US2] Add a generated document link target formatter in `ocrpolish/services/interlinking_service.py`
- [X] T021 [US2] Route language-version links through filename-only target formatting in `ocrpolish/services/interlinking_service.py`
- [X] T022 [US2] Route references-row links through filename-only target formatting in `ocrpolish/services/interlinking_service.py`
- [X] T023 [US2] Route body links through filename-only target formatting in `ocrpolish/services/interlinking_service.py`
- [X] T024 [US2] Preserve existing reference-link resolution, self-link prevention, force-update behavior, and idempotency in `ocrpolish/services/interlinking_service.py`
- [X] T025 [US2] Run `pytest tests/unit/test_interlinking_service.py tests/integration/test_interlink_cli.py` and fix regressions in `ocrpolish/services/interlinking_service.py` or affected tests

**Checkpoint**: User Story 2 is independently functional and testable.

---

## Phase 5: User Story 3 - Preserve All Justified Topic Assignments (Priority: P3)

**Goal**: Metadata tagging no longer imposes a hard topic assignment cap, and resume-derived topic context includes the top 100 topic counter items.

**Independent Test**: Build topic counters with 120 entries and verify 100 preferred topics are passed as context; inspect tagging schema/prompt behavior to verify topic assignments have no hard maximum; process or simulate a dense document response with more than 10 justified topics and verify all are retained.

### Tests for User Story 3

- [X] T026 [P] [US3] Update reuse-hint unit test to expect 100 preferred topics from 120 topic counters in `tests/unit/test_processor_counters.py`
- [X] T027 [P] [US3] Add prompt/schema test proving `topic_tags` guidance has no hard maximum in `tests/unit/test_tagging_service.py`
- [X] T028 [P] [US3] Add aggregation test retaining more than 10 justified topic assignments in `tests/unit/test_tagging_service.py`
- [X] T029 [P] [US3] Add integration test for dense topic assignment retention in `tests/integration/test_tagging_pass.py`

### Implementation for User Story 3

- [X] T030 [US3] Increase resume-derived preferred topic hints to top 100 in `ocrpolish/processor_metadata.py`
- [X] T031 [US3] Remove hard maximum language from topic tag field descriptions in `ocrpolish/models/metadata.py`
- [X] T032 [US3] Remove hard maximum language from tagging prompt instructions while keeping taxonomy-only guidance in `ocrpolish/services/tagging_service.py`
- [X] T033 [US3] Ensure topic aggregation and deduplication retain every justified normalized topic in `ocrpolish/services/tagging_service.py`
- [X] T034 [US3] Run `pytest tests/unit/test_processor_counters.py tests/unit/test_tagging_service.py tests/integration/test_tagging_pass.py` and fix regressions in affected `ocrpolish/` and `tests/` files

**Checkpoint**: User Story 3 is independently functional and testable.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validate the combined feature and keep documentation aligned.

- [X] T035 [P] Update validation notes in `specs/029-fix-tag-interlinks/quickstart.md` if final test commands or expectations change during implementation
- [X] T036 [P] Run focused quickstart validation with `pytest tests/unit/test_tag_parser.py tests/unit/test_interlinking_service.py tests/unit/test_processor_counters.py tests/unit/test_tagging_service.py tests/integration/test_interlink_cli.py tests/integration/test_tagging_pass.py`
- [X] T037 Run full test suite with `pytest` and fix any feature-related regressions in affected `ocrpolish/` or `tests/` files
- [X] T038 Run quality gates `ruff check .`, `ruff format .`, `flake8`, `mypy .`, `coverage run -m pytest`, and `coverage report`; fix feature-related issues in `ocrpolish/`, `tests/`, or `specs/029-fix-tag-interlinks/`
- [X] T039 Review repository status from `.` with `git status --short` and ensure only feature-related files are staged or committed

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup completion and blocks user story work.
- **User Story 1 (Phase 3)**: Depends on Foundational completion.
- **User Story 2 (Phase 4)**: Depends on Foundational completion; can run independently of US1 after fixtures are ready.
- **User Story 3 (Phase 5)**: Depends on Foundational completion; can run independently of US1 and US2 after fixtures are ready.
- **Polish (Phase 6)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: MVP; no dependency on US2 or US3.
- **User Story 2 (P2)**: No dependency on US1 implementation; validates the interlinking service path.
- **User Story 3 (P3)**: No dependency on US1 or US2 implementation; validates metadata tagging and counter context paths.

### Within Each User Story

- Write tests first and confirm they fail for the current behavior.
- Implement the minimal code change for the story.
- Run the story-specific pytest command.
- Stop at the checkpoint before moving to the next story.

### Parallel Opportunities

- T002 and T003 can run in parallel after T001 starts.
- T004, T005, T006, and T007 can run in parallel because they touch different test fixtures.
- T008 and T010 can run in parallel, but T009 shares `tests/unit/test_tag_parser.py` with T008 and should be coordinated.
- T014, T016, T017, T018, and T019 can run in parallel across unit and integration files if edits to `tests/unit/test_interlinking_service.py` are coordinated.
- T026, T027, T028, and T029 can run in parallel if edits to `tests/unit/test_tagging_service.py` are coordinated.
- US1, US2, and US3 implementation phases can proceed in parallel after Phase 2 when different files are assigned.

---

## Parallel Example: User Story 1

```text
Task: "T008 [P] [US1] Add parser contract tests for slash-containing organization and state examples in tests/unit/test_tag_parser.py"
Task: "T010 [P] [US1] Add regression test proving malformed non-slash organization/state tags still warn in tests/unit/test_tag_validation.py"
```

## Parallel Example: User Story 2

```text
Task: "T014 [P] [US2] Add unit test for filename-only language-version links from nested stored paths in tests/unit/test_interlinking_service.py"
Task: "T019 [P] [US2] Add CLI integration regression for nested references-row and body links in tests/integration/test_interlink_cli.py"
```

## Parallel Example: User Story 3

```text
Task: "T026 [P] [US3] Update reuse-hint unit test to expect 100 preferred topics from 120 topic counters in tests/unit/test_processor_counters.py"
Task: "T029 [P] [US3] Add integration test for dense topic assignment retention in tests/integration/test_tagging_pass.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 for slash-containing generated org/state tags.
3. Run `pytest tests/unit/test_tag_parser.py tests/unit/test_tag_validation.py`.
4. Stop and validate the reported malformed-tag warnings are resolved.

### Incremental Delivery

1. Deliver US1 to stop metadata loss from slash-containing entity names.
2. Deliver US2 to make all generated document-to-document interlinks portable.
3. Deliver US3 to remove topic under-tagging and expand topic counter context.
4. Run focused quickstart validation, then full project quality gates.

### Parallel Team Strategy

1. Complete setup and shared fixtures together.
2. Assign US1 to parser-focused work, US2 to interlinking work, and US3 to tagging/counter work.
3. Merge each story only after its independent tests pass.

---

## Notes

- Tests must fail before implementation where they cover current buggy behavior.
- Keep commits atomic and do not stage unrelated working-tree changes.
- Do not edit real data outside `data/`; use temporary fixtures in tests.
- Preserve taxonomy authority: topic counter hints are context, not a source of new taxonomy terms.
