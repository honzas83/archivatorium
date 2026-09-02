# Tasks: Controlled Tag Evolution

**Input**: Design documents from `/specs/041-control-tag-evolution/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Required by the feature specification and plan. Write the story tests first and confirm
that the new assertions fail before implementing their corresponding behavior.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated as
an independent increment. Stage and commit only the files named by the current task or logical task
group; do not include unrelated working-tree changes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files and has no dependency on another
  incomplete task in the same group
- **[Story]**: Maps the task to US1, US2, or US3 from spec.md
- Every task names the exact file or files it changes or validates

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish a safe baseline without modifying user-owned work

- [X] T001 Run the existing focused baseline tests in tests/unit/test_tagging_service.py, tests/unit/test_tag_suppression.py, tests/unit/test_nlp_normalization.py, tests/unit/test_processor_counters.py, tests/unit/test_metadata_reasoning.py, tests/integration/test_model_think_cli.py, tests/integration/test_tagging_pass.py, and tests/integration/test_resume_safety.py and record any pre-existing failures before feature edits

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish the normalized comparison and unconditional entity-collision behavior used by
the document finalizer and vocabulary classification

**⚠️ CRITICAL**: User story implementation starts only after this shared comparison behavior is
tested and available.

- [X] T002 Add failing regression tests for punctuation/case-normalized conceptual identity, every meaningful hierarchical entity-path component, and the rule that protected seed/reused terms cannot bypass entity collisions in tests/unit/test_nlp_normalization.py and tests/unit/test_tag_suppression.py
- [X] T003 Implement canonical conceptual comparison keys and unconditional entity-component collision filtering while preserving the existing topic-overlap policy in archivatorium/utils/nlp.py

**Checkpoint**: Shared normalization and entity separation are deterministic and independently
tested.

---

## Phase 3: User Story 1 - Generate a Focused, Evolving Tag Set (Priority: P1) 🎯 MVP

**Goal**: Produce a compact importance-ranked conceptual-tag list, allow useful novel concepts, and
enforce exact uniqueness, entity separation, 20-total, and five-novel document limits.

**Independent Test**: Feed synthetic single-pass and multi-window model results containing supported
seed/established tags, more than five novel tags, more than 20 total tags, normalized duplicates,
entity names, low-value labels, and combinatorial tag families. Verify the strongest valid tags are
retained in deterministic order, all hard invariants hold, and no extra model call occurs.

### Tests for User Story 1

- [X] T004 [US1] Add failing prompt, seed-versus-novel, exact-deduplication, importance-order, 20-total, five-novel, surplus-novel-skip, empty-stub, and single/multi-window finalization tests in tests/unit/test_tagging_service.py
- [X] T005 [P] [US1] Add failing schema-description tests for the 5–12 target, fewer-when-supported rule, seed-not-allowlist semantics, and unchanged simple conceptual list response in tests/unit/test_metadata_schema.py
- [X] T006 [P] [US1] Add a failing end-to-end generated-Markdown regression proving only the controlled conceptual list is emitted and no provenance fields appear in tests/integration/test_tagging_pass.py

### Implementation for User Story 1

- [X] T007 [P] [US1] Define the model-visible prompt constants and revise conceptual-tag Pydantic descriptions without adding maximum-length validation or provenance fields in archivatorium/models/metadata.py
- [X] T008 [US1] Rewrite conceptual-tag instructions to target 5–12 importance-ranked substantive concepts, prefer equivalent seed/established forms, permit distinct novel tags, reject padding, passing mentions, synonym/variant expansion, entity names, and combinatorial families, and apply the same rules to acronyms in archivatorium/services/tagging_service.py
- [X] T009 [US1] Implement one ordered conceptual-tag finalizer for both inference paths that normalizes, filters, removes entity/topic collisions, exactly deduplicates, classifies against the seed-plus-established snapshot, skips novel candidates beyond five while continuing to consider known candidates, and caps final output at 20 in archivatorium/services/tagging_service.py
- [X] T010 [US1] Replace the windowed top-100 shortcut with deterministic aggregate ranking by frequency, best local importance rank, and first-seen position before the shared document finalizer in archivatorium/services/tagging_service.py
- [X] T011 [US1] Run and pass the independent US1 suite in tests/unit/test_tagging_service.py, tests/unit/test_tag_suppression.py, tests/unit/test_nlp_normalization.py, tests/unit/test_metadata_schema.py, and tests/integration/test_tagging_pass.py

**Checkpoint**: US1 is independently usable as the MVP; tag lists are prompt-focused and hard-bounded
without structured provenance or additional model calls.

---

## Phase 4: User Story 2 - Evolve Vocabulary Without Feedback Amplification (Priority: P2)

**Goal**: Retain first-occurrence novel tags locally, but promote them into preferred vocabulary only
after two independent document occurrences, including occurrences reconstructed from existing
archive output.

**Independent Test**: Process or scan documents sequentially and verify that repeated text within one
document counts once, a one-document tag is absent from later reuse hints, its second independent
document is generated without prior promotion, and only subsequent documents receive it as an
established preferred tag; seed tags remain available at zero occurrences and established tags do
not demote during the run.

### Tests for User Story 2

- [X] T012 [US2] Add failing counter lifecycle tests for one-document isolation, same-document deduplication, preflight promotion at two files, post-write promotion, deterministic established ordering, full established-vocabulary availability, and run-scoped no-demotion after overwrite subtraction in tests/unit/test_processor_counters.py
- [X] T013 [P] [US2] Add failing resume/preflight regressions proving skipped documents are not double-counted, support files do not promote tags, and two existing archive documents establish a tag without migration in tests/integration/test_resume_safety.py

### Implementation for User Story 2

- [X] T014 [US2] Add the two-document promotion threshold and run-scoped monotonic established conceptual-tag set, populate it during preflight and successful generated-output ingestion, and preserve it across counter subtraction in archivatorium/processor_metadata.py
- [X] T015 [US2] Build preferred conceptual reuse hints exclusively from the complete established set in deterministic count-descending/name-ascending order while leaving one-off tags local and seed availability owned by TaggingService in archivatorium/processor_metadata.py
- [X] T016 [US2] Run and pass the independent US2 lifecycle suite in tests/unit/test_processor_counters.py and tests/integration/test_resume_safety.py

**Checkpoint**: US2 independently demonstrates controlled vocabulary evolution from existing and
new archive documents without a registry, migration, automatic rewrite, or feedback amplification.

---

## Phase 5: User Story 3 - Control Reasoning for Tag Inference (Priority: P3)

**Goal**: Apply the metadata command's existing typed `--model-think` value to every tag-inference
request while preserving the current inference-call count.

**Independent Test**: Invoke metadata with `False`, `low`, `medium`, and `high`, including mixed-case
spellings and the omitted default, and inspect mocked single-pass and multi-window calls to verify
that every tag request receives the correctly typed value and that the number of calls remains one
per existing inference window.

### Tests for User Story 3

- [X] T017 [US3] Add failing parameterized unit tests for the TaggingService default and explicit typed reasoning values plus identical reasoning and unchanged call count across every window in tests/unit/test_metadata_reasoning.py and tests/unit/test_tagging_service.py
- [X] T018 [P] [US3] Extend metadata CLI tests to assert that case-insensitive `False`, `low`, `medium`, `high`, and the default `medium` reach both MetadataProcessor and TaggingService with correct types in tests/integration/test_model_think_cli.py

### Implementation for User Story 3

- [X] T019 [US3] Add typed `model_think` constructor state with the shared `medium` default and replace hard-coded `think=False` at the sole tag extraction boundary in archivatorium/services/tagging_service.py
- [X] T020 [US3] Pass the converted metadata-command reasoning value into TaggingService and update option help to cover metadata and tag inference in archivatorium/cli.py
- [X] T021 [US3] Run and pass the independent US3 suite in tests/unit/test_metadata_reasoning.py, tests/unit/test_tagging_service.py, and tests/integration/test_model_think_cli.py

**Checkpoint**: US3 independently proves command-scoped reasoning reaches all and only the existing
tag-inference calls.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Document the completed behavior and validate all stories together

- [ ] T022 [P] Document seed vocabulary, two-document promotion, 5–12 prompt target, hard limits, entity precedence, rerun adoption, and metadata/tag reasoning semantics in README.md
- [ ] T023 Run the complete focused workflow from specs/041-control-tag-evolution/quickstart.md and reconcile any cross-story regression only in the feature-owned source and test paths named in this task list
- [ ] T024 Run `ruff check .`, `ruff format --check .`, `flake8 archivatorium tests --max-cognitive-complexity=10`, `mypy .`, `pytest`, `coverage run -m pytest`, and `coverage report`; fix feature-caused failures only in archivatorium/, tests/, and README.md without staging unrelated working-tree changes

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; captures the pre-change baseline.
- **Foundational (Phase 2)**: Depends on T001 and blocks US1 finalization behavior.
- **US1 (Phase 3)**: Depends on T002–T003. It establishes the shared finalizer consumed by the
  seed/established vocabulary snapshot.
- **US2 (Phase 4)**: Depends on the US1 known-versus-novel boundary from T009 but can develop its
  processor tests in parallel with later US1 service work.
- **US3 (Phase 5)**: Depends only on setup and can be implemented independently of US1/US2 after the
  baseline, although sequential priority order is recommended.
- **Polish (Phase 6)**: Depends on every story selected for delivery.

### User Story Dependencies

- **US1 (P1)**: Begins after the shared normalization foundation; no dependency on US2 or US3.
- **US2 (P2)**: Uses US1's vocabulary snapshot classification but is independently testable through
  processor counters and reuse hints.
- **US3 (P3)**: No functional dependency on US1 or US2; it changes only request configuration and CLI
  propagation.

### Within Each User Story

- Write the story's tests first and verify the new assertions fail for the intended reason.
- Implement model/schema descriptions before prompt/service behavior that consumes them.
- Implement normalization and finalization before aggregate-window ranking.
- Implement promotion state before filtering and ordering reuse hints.
- Implement TaggingService reasoning state before wiring it from the CLI.
- Pass the independent story suite before proceeding to the next priority.

### Parallel Opportunities

- T004, T005, and T006 can be authored in parallel in different test files.
- After the US1 tests exist, T007 can run in parallel with T008–T010 because it changes the model
  descriptions rather than the service implementation.
- T012 and T013 can be authored in parallel in unit and integration test files.
- T017 and T018 can be authored in parallel in unit and integration test files.
- US3 can be implemented in parallel with US2 after T001 because their production paths are
  separate until final validation.
- T022 can run in parallel with the final focused test pass after behavior is stable.

---

## Parallel Example: User Story 1

```text
Task T004: Add TaggingService prompt/finalizer/window tests in tests/unit/test_tagging_service.py
Task T005: Add schema-description tests in tests/unit/test_metadata_schema.py
Task T006: Add generated-Markdown contract test in tests/integration/test_tagging_pass.py
```

## Parallel Example: User Story 2

```text
Task T012: Add promotion lifecycle unit tests in tests/unit/test_processor_counters.py
Task T013: Add archive-resume promotion tests in tests/integration/test_resume_safety.py
```

## Parallel Example: User Story 3

```text
Task T017: Add direct service reasoning tests in tests/unit/test_metadata_reasoning.py and tests/unit/test_tagging_service.py
Task T018: Add CLI propagation tests in tests/integration/test_model_think_cli.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete T001–T003 for baseline and shared normalization.
2. Complete T004–T010 for focused prompt behavior and hard document limits.
3. Run T011 and inspect the final controlled tag list independently.
4. Stop here for an MVP that directly prevents the reported tag explosion while retaining up to
   five useful novel tags.

### Incremental Delivery

1. **Foundation + US1**: Enforce concise tag output and deterministic safety boundaries.
2. **Add US2**: Prevent one-off feedback amplification and promote at two documents.
3. **Add US3**: Give every tag window the metadata command's reasoning setting.
4. **Polish**: Update documentation and pass the full constitutional quality suite.

### Atomic Commit Strategy

- Commit T002–T003 as the shared normalized-collision foundation.
- Commit each story's failing tests before its implementation where practical.
- Commit US1, US2, and US3 implementations as separate stable increments.
- Commit documentation separately after behavior is verified.
- Use explicit path staging for every commit; never use broad staging while unrelated modifications
  or archive datasets are present.

## Notes

- `[P]` tasks operate on different files and can proceed concurrently at that point in the graph.
- `USEFUL_TAGS.yaml` remains a seed and is not modified by this feature.
- Exact normalization does not attempt semantic alias or synonym resolution; the strengthened LLM
  prompt owns those judgments.
- Existing archive Markdown remains unchanged until the user explicitly reruns metadata processing.
- No task adds structured tag provenance or an additional model call.
