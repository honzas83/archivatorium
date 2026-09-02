# Tasks: NATO Topic Taxonomy V2

**Input**: Design documents from `/specs/039-nato-taxonomy-v2/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: The feature specification explicitly requires taxonomy, classifier-context, false-positive,
positive-example, recursive CLI, and compatibility validation. Test tasks precede their corresponding
implementation tasks.

**Organization**: Tasks are grouped by user story so each story produces an independently testable
increment. Real NATO documents and review outputs remain under gitignored
`data/039-nato-taxonomy-v2/`.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it changes different files and does not depend on unfinished
  work in the same phase.
- **[Story]**: Maps the task to a user story from spec.md.
- Every task includes an exact file path and must finish with a stable, feature-only commit as required
  by the constitution.

## Phase 1: Setup (Shared Test Infrastructure)

**Purpose**: Replace tests that rely on missing YAML files with reusable, valid taxonomy inputs.

- [X] T001 Add reusable minimal legacy and schema-v2 taxonomy fixtures, including policy and useful-tag files, in tests/conftest.py

---

## Phase 2: Foundational (Blocking Taxonomy Safety)

**Purpose**: Establish strict taxonomy loading and approved-path invariants used by every story.

**⚠️ CRITICAL**: No user story implementation begins until this phase passes.

- [X] T002 [P] Add failing tests for root/category/topic types, blank descriptions, invalid sample blocks, slash-containing components, normalized path collisions, and missing schema-v2 policy in tests/unit/test_flattening.py
- [X] T003 Implement TaxonomyValidationError plus common legacy and schema-v2 validation in archivatorium/services/flattening_service.py, preserving the legacy `category` and `topic` YAML keys
- [X] T004 [P] Add failing tests for unreadable/invalid hierarchy files and construction of the normalized approved-topic set in tests/unit/test_tagging_service.py
- [X] T005 Propagate actionable hierarchy loading/validation failures and initialize the approved normalized topic IDs once per run in archivatorium/services/tagging_service.py

**Checkpoint**: Malformed hierarchies fail before classification, while the unchanged v1 hierarchy
loads successfully and exposes a non-empty approved-path set.

---

## Phase 3: User Story 1 - Classify Documents by Substantive Subject (Priority: P1) 🎯 MVP

**Goal**: Apply one universal important-subject threshold, prefer omission for marginal matches, and
allow administrative or unmatched documents to receive no thematic topics.

**Independent Test**: With a synthetic valid hierarchy and mocked model results, inspect both
single-pass and sliding-window prompts for the universal policy; confirm empty topic lists are valid
and unsupported topic paths never enter aggregated output.

### Tests for User Story 1

- [X] T006 [US1] Add failing single-pass and sliding-window tests for substantive-subject wording, incidental mentions, administrative empty-topic output, unknown paths, and earliest supported-path deduplication in tests/unit/test_tagging_service.py

### Implementation for User Story 1

- [X] T007 [US1] Align TopicResult, WindowTaggingResult, and AggregatedTaggingResult field descriptions with all-substantive-but-not-marginal selection and valid empty topic lists in archivatorium/models/metadata.py
- [X] T008 [US1] Build the effective legacy/v2 classification policy, inject it into the main and critical prompt rules, and filter normalized model topics against approved IDs without extra model calls in archivatorium/services/tagging_service.py
- [X] T009 [US1] Add a mocked integration test proving incidental/administrative content can yield no topics while a supported substantive topic survives in tests/integration/test_nato_topic_policy.py

**Checkpoint**: User Story 1 passes independently with no quotation verifier, retry behavior, or
additional model request.

---

## Phase 4: User Story 2 - Distinguish Overlapping Nuclear and Alliance Topics (Priority: P1)

**Goal**: Provide the complete six-category, 55-topic NATO v2 hierarchy with narrow definitions and
counterexamples for the known confused subjects.

**Independent Test**: Load the v2 file and assert exact category/topic counts and placements, absence
of the two overloaded v1 labels, the required corrected positive/negative examples, unique normalized
paths, and the unchanged v1 checksum.

### Tests for User Story 2

- [X] T010 [US2] Add failing tests for the six exact categories, 55 unique topic paths, required splits/renames/moves, corrected confusable examples, old-label absence, and v1 SHA-256 `90daa6f599decda1c6fed633a83b99d95362a59abb2eac4e9c1d61a6f4bf515a` in tests/unit/test_nato_taxonomy_v2.py

### Implementation for User Story 2

- [X] T011 [US2] Create the complete schema-v2 classification policy and 55-topic hierarchy with the reviewed definitions and counterexamples in topics/NATO_themes_v2.yaml without modifying topics/NATO_themes.yaml
- [X] T012 [US2] Run representative positive and negative cases for every split, renamed, moved, or tightened topic and record the local review outcome in data/039-nato-taxonomy-v2/reports/topic-distinction-review.md

**Checkpoint**: User Story 2 independently distinguishes guarantees from deployment, release from
strike planning, consultation from meeting form, and command structure from infrastructure.

---

## Phase 5: User Story 3 - Use Complete Taxonomy Context (Priority: P2)

**Goal**: Preserve every classification-relevant category and topic field and present the complete
policy-plus-topic object to the classifier.

**Independent Test**: Flatten a synthetic multi-category hierarchy and verify that each item contains
its canonical ID, category, full category description, topic description, and all positive and
negative samples; inspect one generated prompt to verify the effective policy and full topic list are
serialized exactly once.

### Tests for User Story 3

- [X] T013 [US3] Add failing tests for category/category-description preservation, complete ordered sample lists, and compatibility of the existing topic `description` key in tests/unit/test_flattening.py
- [X] T014 [US3] Add failing tests that the prompt payload contains the effective classification policy and full flattened topic context exactly once in tests/unit/test_tagging_service.py

### Implementation for User Story 3

- [X] T015 [US3] Extend flattened topic records with canonical category and complete category_description while retaining every non-empty topic sample in archivatorium/services/flattening_service.py
- [ ] T016 [US3] Serialize the classifier prompt payload as classification_policy plus topics without editorial root fields in archivatorium/services/tagging_service.py

**Checkpoint**: User Story 3 proves 100% of v2 topic definitions retain their category context,
descriptions, and examples at the classifier boundary.

---

## Phase 6: User Story 4 - Adopt V2 by Rerunning Metadata (Priority: P3)

**Goal**: Keep v1 reproducible and let maintainers explicitly rerun recursive metadata extraction with
v2 into a separate output directory.

**Independent Test**: Invoke the CLI with synthetic nested input trees and explicit v1/v2 hierarchy
paths; confirm the selected hierarchy reaches TaggingService, relative paths remain recursive, v2
output contains only approved v2 paths, and prior v1 output is not rewritten.

### Tests for User Story 4

- [ ] T017 [US4] Add CLI integration coverage for explicit v1/v2 hierarchy selection, recursive nested inputs, separate output directories, approved v2 paths, and invalid-hierarchy failure in tests/integration/test_nato_taxonomy_selection.py

### Implementation for User Story 4

- [ ] T018 [P] [US4] Document explicit v1 and v2 metadata commands, separate-output reruns, unchanged-v1 guarantees, and the absence of path migration in README.md
- [ ] T019 [US4] Execute fresh local v1 and v2 metadata runs against data/039-nato-taxonomy-v2/input/ and record command/outcome comparisons in data/039-nato-taxonomy-v2/reports/rerun-comparison.md

**Checkpoint**: User Story 4 demonstrates opt-in v2 adoption by reprocessing source documents, with
no default switch, migration map, or old-output mutation.

---

## Phase 7: Polish & Cross-Cutting Validation

**Purpose**: Validate measurable outcomes, compatibility, documentation, and repository quality.

- [ ] T020 [P] Score the reviewed NATO corpus for SC-001 through SC-006 and record accuracy, challenged-case correction, renamed/split-topic recall, and administrative empty-topic rates in data/039-nato-taxonomy-v2/reports/quality-score.md
- [ ] T021 Re-run the commands and expected outcomes in specs/039-nato-taxonomy-v2/quickstart.md and correct that guide if the implemented interface differs
- [ ] T022 Run ruff, formatting, flake8 complexity, mypy, pytest, and coverage gates across archivatorium/ and tests/, recording any environment-only limitations in specs/039-nato-taxonomy-v2/quickstart.md
- [ ] T023 Verify `git diff --exit-code -- topics/NATO_themes.yaml`, confirm its SHA-256 remains `90daa6f599decda1c6fed633a83b99d95362a59abb2eac4e9c1d61a6f4bf515a`, and inspect git status to ensure data/ and unrelated working-tree files are not staged

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Starts immediately.
- **Foundational (Phase 2)**: Depends on T001 and blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Phase 2 and is the MVP.
- **User Story 2 (Phase 4)**: Depends on Phase 2. It can be implemented independently of US1, but a
  sequential run should complete US1 first because both validate the substantive-subject policy.
- **User Story 3 (Phase 5)**: Depends on Phase 2. T016 shares `tagging_service.py` with US1, so execute
  it after T008 when working sequentially.
- **User Story 4 (Phase 6)**: Depends on the v2 file from T011 and full prompt context from T016.
- **Polish (Phase 7)**: Depends on all selected user stories; corpus scoring also requires T019.

### User Story Dependency Graph

```text
Setup -> Foundation -> US1 (MVP)
                    -> US2 ----\
                    -> US3 -----+-> US4 -> Polish
```

US1, US2, and the test preparation portion of US3 can begin after the foundation. US4 requires the
integrated v2 taxonomy and classifier context.

### Within Each User Story

- Write the listed tests first and confirm the new assertions fail for the intended reason.
- Implement the smallest change that satisfies the story and rerun its focused tests.
- Keep taxonomy/file validation outside the model-call loop.
- Commit only the paths named by the completed task; never stage unrelated tests, datasets, or helper
  scripts already present in the working tree.

## Parallel Opportunities

- After T001, T002 and T004 can be written in parallel because they modify different unit-test files.
- After Phase 2, US1 and US2 can proceed in parallel; avoid concurrent edits to
  `tagging_service.py` when US3 begins.
- T018 documentation can run in parallel with the US4 integration test after the CLI contract is
  understood.
- T020 can run in parallel with documentation verification once the local v2 run is complete.

## Parallel Example: User Stories 1 and 2

```text
Task A: T006-T009 implement and validate the universal substantive-subject behavior.
Task B: T010-T012 validate and create the complete NATO v2 taxonomy.
```

## Parallel Example: User Story 4

```text
Task A: T017 add explicit hierarchy-selection and recursive rerun integration coverage.
Task B: T018 document the v1/v2 rerun workflow in README.md.
```

## Implementation Strategy

### MVP First: User Story 1

- Complete T001-T005 for safe hierarchy loading and approved-path setup.
- Complete T006-T009 for conservative topic selection and valid empty topic output.
- Stop and run the US1 focused tests before adding the full NATO v2 content.

### Incremental Delivery

- Add US2 to deliver the complete 55-topic hierarchy and validate the known distinctions.
- Add US3 to prove all category/topic guidance reaches classification.
- Add US4 to validate explicit recursive reruns with isolated outputs.
- Complete cross-cutting corpus scoring and all constitutional quality gates.

### Task Completion Discipline

- Every task must leave its named tests passing and the repository in a stable state.
- Every completed task receives a small logical commit containing only its relevant files.
- Local `data/039-nato-taxonomy-v2/` artifacts remain untracked and must never enter a commit.
