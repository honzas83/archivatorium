# Tasks: Hierarchical Person Entities and Model Reasoning Control

**Input**: Design documents from `/specs/040-person-hierarchy-model-think/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Test tasks are included because the specification defines measurable validation outcomes
and the implementation follows test-first development.

**Organization**: Tasks are grouped by user story so Person generation, model reasoning control, and
downstream Person navigation can be implemented and validated as independent increments.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it affects different files and has no dependency on another
  incomplete task in the same phase.
- **[Story]**: Maps the task to a user story from spec.md.
- Every task names the exact file or files it changes.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm that the existing Python CLI structure and quality tooling can be reused.

No setup changes are required. The project already provides Click, Pydantic, Ollama integration,
pytest/coverage, ruff, flake8, and mypy, and the feature documentation is committed on its branch.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Identify shared work that must block every user story.

No cross-story foundation is required. The Person normalizer belongs to User Story 1 and is reused
by User Story 3; the reasoning-value converter belongs to the independently deliverable User Story 2.

**Checkpoint**: User Stories 1 and 2 can begin independently.

---

## Phase 3: User Story 1 - Generate Canonical Person Paths (Priority: P1) 🎯 MVP

**Goal**: Generate surname-first Person paths, allow surname-only identity, compact initials, and
exclude titles and roles.

**Independent Test**: Synthetic tagging candidates produce `Person/Andrae/KW`,
`Person/Luns/Joseph`, and `Person/Andrae` as appropriate; malformed, over-deep, or role-bearing
candidates are omitted.

### Tests for User Story 1

> **NOTE: Write these tests first and confirm they fail before implementation.**

- [ ] T001 [P] [US1] Add failing unit cases for full names, surname-only names, K-W/K. W. initials, compound names, role modifiers, missing surnames, and excessive depth in tests/unit/test_person_entities.py
- [ ] T002 [P] [US1] Add failing prompt and aggregation cases for surname-first output, initials, surname-only identity, role exclusion, deduplication, and malformed-candidate warnings in tests/unit/test_person_tagging.py

### Implementation for User Story 1

- [ ] T003 [US1] Implement shared Person path parsing, component validation, tag normalization, initials compaction, and prohibited-modifier rejection in archivatorium/utils/person_entities.py
- [ ] T004 [P] [US1] Change model-visible entity field descriptions to `Person/<surname>[/<given-name-or-initials>]` in archivatorium/models/metadata.py
- [ ] T005 [US1] Update Person instructions/examples and normalize every generated Person candidate before single-pass or windowed aggregation in archivatorium/services/tagging_service.py

**Checkpoint**: Newly generated Person candidates satisfy the Person path contract independently of
Markdown parsing and indexing.

---

## Phase 4: User Story 2 - Select Model Reasoning Effort (Priority: P2)

**Goal**: Let users select disabled, low, medium, or high reasoning for the specified OCR and
metadata model calls, with a medium default.

**Independent Test**: Both commands accept every case-insensitive choice, reject unsupported values
before processing, and mocked governed model requests receive the correctly typed value while
tagging and unrelated OCR profiles retain their prior behavior.

### Tests for User Story 2

> **NOTE: Write these tests first and confirm they fail before implementation.**

- [ ] T006 [P] [US2] Add failing conversion, help/default, case-insensitive choice, and pre-processing rejection tests for both commands in tests/integration/test_model_think_cli.py
- [ ] T007 [P] [US2] Add failing primary extraction, conditional date extraction, retry propagation, default-medium, and tagging-isolation tests in tests/unit/test_metadata_reasoning.py
- [ ] T008 [P] [US2] Add failing Qwen 3.8 default/override and unchanged standard, GLM, FireRed, retry, and reasoning-stripping cases in tests/unit/test_ocr_reasoning.py, updating former high-default expectations in tests/unit/test_ocr_engine.py and tests/integration/test_ocr_cli.py

### Implementation for User Story 2

- [ ] T009 [US2] Implement the shared `False|low|medium|high` reasoning type and case-insensitive CLI conversion in archivatorium/utils/model_think.py
- [ ] T010 [P] [US2] Change the Qwen 3.8 default to medium and add a Qwen-only per-run reasoning override while preserving other mode profiles in archivatorium/ocr_engine.py
- [ ] T011 [P] [US2] Store the command-scoped reasoning setting and pass it to primary and conditional date structured extraction calls in archivatorium/processor_metadata.py
- [ ] T012 [US2] Add `--model-think` to the metadata and OCR commands and pass the converted setting to their processor/engine boundaries in archivatorium/cli.py

**Checkpoint**: User Story 2 works independently from Person hierarchy changes and does not alter
tag extraction or unrelated OCR-mode reasoning behavior.

---

## Phase 5: User Story 3 - Preserve Navigable Person Metadata (Priority: P3)

**Goal**: Preserve surname-only and surname-plus-given Person paths through parsing, counters,
document output, XLSX export, and surname-grouped People indexes.

**Independent Test**: A generated `Entities/Person/Andrae/KW` path survives every archive consumer,
appears under A in the People index, and remains distinct from other people sharing Andrae; a
surname-only `Entities/Person/Andrae` remains valid.

### Tests for User Story 3

> **NOTE: Write these tests first and confirm they fail before implementation.**

- [ ] T013 [P] [US3] Add failing parser and validation cases for both valid Person depths, compacted initials, complete raw paths, lowercased counter values, and rejected extra depth in tests/unit/test_tag_parser.py and tests/unit/test_tag_validation.py
- [ ] T014 [P] [US3] Add failing People-index cases for surname ordering, surname alphabetic headings, surname-only paths, and shared surnames in tests/unit/test_markdown_indices.py and tests/unit/test_indexing_service.py
- [ ] T015 [P] [US3] Add a failing synthetic end-to-end case covering tagging, entity sections, preflight counters/reuse hints, and XLSX raw paths in tests/integration/test_person_entity_hierarchy.py

### Implementation for User Story 3

- [ ] T016 [P] [US3] Extend canonical Person validation to accept surname-only and surname-plus-given paths and retain the full normalized identity in archivatorium/utils/tag_parser.py
- [ ] T017 [P] [US3] Specialize People-index sorting, labels, and alphabetic grouping on the surname component without changing other indexes in archivatorium/services/indexing_service.py

**Checkpoint**: All three user stories are independently testable and the complete Person hierarchy
survives the archive pipeline.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Document the final interface, validate end-to-end behavior, and enforce project quality
and repository-isolation requirements.

- [ ] T018 [P] Document the Person path forms, initials behavior, excluded role modifiers, metadata rerun adoption, and `--model-think` examples/default/scope in README.md
- [ ] T019 Run every scenario and focused command in specs/040-person-hierarchy-model-think/quickstart.md and correct the guide if the implemented interface differs
- [ ] T020 Run ruff lint/format, flake8 complexity, mypy, pytest, and coverage gates across archivatorium/ and tests/ and record any environment or pre-existing baseline limitations in specs/040-person-hierarchy-model-think/quickstart.md
- [ ] T021 Inspect `git status --short` and staged paths after validation, remove only feature-created transient artifacts, and confirm unrelated modified tests, archive datasets, and data/ files were not staged

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No changes required.
- **Foundational (Phase 2)**: No shared blocker; User Stories 1 and 2 may start immediately.
- **User Story 1 (Phase 3)**: Starts immediately and provides the Person normalizer required by
  User Story 3.
- **User Story 2 (Phase 4)**: Starts immediately and is independent of User Stories 1 and 3.
- **User Story 3 (Phase 5)**: Depends on User Story 1, especially T003 and T005.
- **Polish (Phase 6)**: Depends on all selected user stories being complete.

### User Story Dependencies

```text
US1 (P1) ─────────→ US3 (P3)

US2 (P2) ───────────────────→ Polish
US1 + US3 ──────────────────→ Polish
```

- **US1**: No story dependency; delivers the MVP generation contract.
- **US2**: No story dependency; can be implemented in parallel with US1.
- **US3**: Depends on US1's canonical generated paths and shared normalizer.

### Within Each User Story

- Write the story's tests and confirm they fail for the intended missing behavior.
- Implement shared value/normalization logic before callers.
- Implement service or processor behavior before CLI/end-to-end integration.
- Run the complete story-specific test set at its checkpoint.
- Commit each completed task atomically, staging only its named paths.

### Parallel Opportunities

- T001 and T002 can run in parallel.
- After the US1 tests fail, T003 and T004 can run in parallel; T005 follows both.
- T006, T007, and T008 can run in parallel.
- After T009, T010 and T011 can run in parallel; T012 follows both.
- T013, T014, and T015 can be authored in parallel after US1.
- T016 and T017 can run in parallel after their corresponding failing tests.
- T018 can run in parallel with focused implementation verification before T019–T021.
- US1 and US2 can be implemented in parallel by separate contributors.

---

## Parallel Example: User Story 1

```text
Task T001: Add Person normalization tests in tests/unit/test_person_entities.py
Task T002: Add Person prompt/aggregation tests in tests/unit/test_person_tagging.py

After those tests fail:
Task T003: Implement archivatorium/utils/person_entities.py
Task T004: Update archivatorium/models/metadata.py
```

## Parallel Example: User Story 2

```text
Task T006: Add CLI contract tests in tests/integration/test_model_think_cli.py
Task T007: Add metadata request tests in tests/unit/test_metadata_reasoning.py
Task T008: Add OCR request tests in tests/unit/test_ocr_reasoning.py

After T009 defines the shared value conversion:
Task T010: Implement OCR propagation in archivatorium/ocr_engine.py
Task T011: Implement metadata propagation in archivatorium/processor_metadata.py
```

## Parallel Example: User Story 3

```text
Task T013: Add parser/validation tests
Task T014: Add People-index tests
Task T015: Add archive-pipeline integration test

After the tests fail:
Task T016: Extend archivatorium/utils/tag_parser.py
Task T017: Update archivatorium/services/indexing_service.py
```

---

## Implementation Strategy

### MVP First: User Story 1

- Complete T001–T005.
- Verify new generation produces surname-first, initials-compacted, role-free paths.
- Stop and validate the story independently before downstream parser/index changes.

### Incremental Delivery

- **Increment 1 — US1**: Canonical Person generation and validation.
- **Increment 2 — US2**: Independent model reasoning CLI control.
- **Increment 3 — US3**: Parser, export, counter, and People-index preservation.
- **Increment 4 — Polish**: Documentation, quickstart, all quality gates, and staging audit.

### Safe Worktree Strategy

- Do not edit the user-modified `tests/integration/test_cli.py`,
  `tests/integration/test_metadata_command.py`, or `tests/unit/test_metadata_processor.py`; use the
  dedicated feature test modules named above.
- Before every commit, inspect staged paths and exclude all unrelated working-tree files.
- Do not add archive datasets, generated outputs, or optional `data/` validation material to Git.

## Notes

- `[P]` tasks modify different files and have no dependency on incomplete sibling tasks.
- `[US1]`, `[US2]`, and `[US3]` provide requirement-to-story traceability.
- Tests precede implementation and must fail for the intended missing behavior, not environment
  setup problems.
- Existing archive files remain unchanged; rerunning metadata is the adoption path.
- No task adds model calls, migrates Person paths, changes tag-extraction reasoning, or broadens the
  OCR override beyond Qwen 3.8.
