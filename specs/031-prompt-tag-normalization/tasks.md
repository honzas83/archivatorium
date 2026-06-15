# Tasks: Prompt Tag Normalization

**Input**: Design documents from `specs/031-prompt-tag-normalization/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/tagging-prompt-contract.md](./contracts/tagging-prompt-contract.md), [quickstart.md](./quickstart.md)

**Tests**: No test-code changes. Existing tests may be run for regression only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing. Implementation work must stay limited to LLM prompt/context behavior.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it touches different files or only reads context
- **[Story]**: User story label (`US1`, `US2`, `US3`) for story phases only
- Every task includes an exact file path or repository path

## Phase 1: Setup (Shared Context)

**Purpose**: Verify the current prompt location and corrected scope before editing.

- [X] T001 Inspect current LLM tagging prompt literal/content in `ocrpolish/services/tagging_service.py`
- [X] T002 [P] Inspect prompt contract requirements in `specs/031-prompt-tag-normalization/contracts/tagging-prompt-contract.md`
- [X] T003 [P] Inspect analysis findings in `docs/tag_analysis_report.md` and `COUNTS_v6.csv`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Lock the no-code-change boundary before any story work begins.

**CRITICAL**: No user story work should begin until this phase is complete.

- [X] T004 Confirm implementation scope is limited to LLM prompt text in `ocrpolish/services/tagging_service.py`
- [X] T005 Confirm no planned edits to tests, schemas, CLI, taxonomy files, useful-tags files, parsers, metadata rendering, indexing, or interlinking in repository path `.`

**Checkpoint**: Foundation ready; user story implementation can now proceed.

---

## Phase 3: User Story 1 - Normalize Repeated Entities (Priority: P1) MVP

**Goal**: The LLM prompt instructs generated entity tags to converge on English canonical forms with consistent casing and hierarchy.

**Independent Test**: Inspect the generated prompt text and verify it includes rules/examples for NATO/nato/OTAN, Bruxelles/Brussels, Allemagne/Germany, USA/United States, title casing, standard acronyms, and `City/<country>/<city>` hierarchy.

### Implementation for User Story 1

- [X] T006 [US1] Update only the LLM prompt text in `ocrpolish/services/tagging_service.py` to require English canonical forms for states, organisations, and cities when the intended entity is clear
- [X] T007 [US1] Update only the LLM prompt text in `ocrpolish/services/tagging_service.py` to require title case while preserving standard all-caps acronyms
- [X] T008 [US1] Add only prompt-text examples for NATO/OTAN, Brussels/Bruxelles, Germany/Allemagne, and United States/USA in `ocrpolish/services/tagging_service.py`
- [X] T009 [US1] Inspect generated prompt text from `ocrpolish/services/tagging_service.py` and verify User Story 1 contract items are present

**Checkpoint**: User Story 1 is complete and independently testable as the MVP.

---

## Phase 4: User Story 2 - Recover Obvious OCR-Damaged Entities (Priority: P2)

**Goal**: The LLM prompt asks the model to correct obvious OCR-damaged entity names only when context clearly identifies the intended entity.

**Independent Test**: Inspect the generated prompt text and verify it includes conservative OCR recovery guidance plus abstract examples for recurring organisation-name OCR damage.

### Implementation for User Story 2

- [X] T010 [US2] Add only prompt-text OCR recovery instructions to `ocrpolish/services/tagging_service.py`
- [X] T011 [US2] Add only prompt-text recurring-organisation OCR-damage examples to `ocrpolish/services/tagging_service.py`
- [X] T012 [US2] Add only prompt-text ambiguity guard wording to `ocrpolish/services/tagging_service.py`
- [X] T013 [US2] Inspect generated prompt text from `ocrpolish/services/tagging_service.py` and verify User Story 2 contract items are present

**Checkpoint**: User Stories 1 and 2 both work independently through prompt inspection.

---

## Phase 5: User Story 3 - Preserve Useful Substantive Tags While Reducing Noise (Priority: P3)

**Goal**: The LLM prompt reduces malformed duplicate tags without weakening justified topic evidence, conceptual tag reuse, or meaningful acronym preservation.

**Independent Test**: Inspect the generated prompt text and verify it still requires direct quoted evidence for topic reasons, useful/resumed vocabulary reuse for conceptual tags, inclusion of meaningful acronyms, and title-casing of non-acronym all-caps terms.

### Implementation for User Story 3

- [X] T014 [US3] Refine only conceptual-tag prompt text in `ocrpolish/services/tagging_service.py` without changing minimum conceptual tag requirements
- [X] T015 [US3] Ensure topic evidence prompt text remains unchanged or stronger in `ocrpolish/services/tagging_service.py`
- [X] T016 [US3] Inspect generated prompt text from `ocrpolish/services/tagging_service.py` and verify User Story 3 contract items are present

**Checkpoint**: All user stories are independently covered by prompt inspection.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verify the LLM-prompt-only boundary and run regression checks without editing non-prompt code.

- [X] T017 [P] Confirm no test, CLI option, schema, taxonomy, useful-tags, parser, metadata renderer, indexing, or interlinking changes were made by reviewing `git diff -- ocrpolish tests`
- [X] T018 [P] Compare prompt text against `specs/031-prompt-tag-normalization/contracts/tagging-prompt-contract.md` and update only LLM prompt text in `ocrpolish/services/tagging_service.py` if any required prompt item is missing
- [X] T019 Run `pytest tests/unit/test_tagging_service.py` at repository path `.` for regression only
- [X] T020 Run `pytest tests/integration/test_metadata_command.py` at repository path `.` for regression only
- [ ] T021 Run `ruff check .` at repository path `.` for regression only
- [ ] T022 Run `ruff format --check .` at repository path `.` for regression only
- [ ] T023 Run `mypy .` at repository path `.` for regression only

---

## Phase 7: User Story 4 - Use Relative Filename Context (Priority: P4)

**Goal**: The LLM prompt includes the full source-relative filename so archival code, document year/date, series, and folder context can inform tagging when consistent with the full document text.

**Independent Test**: Inspect the generated prompt text for a nested source document and verify it includes the full relative filename before the full document text.

### Implementation for User Story 4

- [X] T024 [US4] Pass source-relative filename context from `ocrpolish/processor_metadata.py` into tag extraction without changing CLI options, schemas, output rendering, parsers, taxonomy files, or useful-tags files
- [X] T025 [US4] Add source-relative filename prompt context to `ocrpolish/services/tagging_service.py`
- [X] T026 [US4] Add prompt guidance in `ocrpolish/services/tagging_service.py` that filename context may inform archival code, document year/date, series, and collection context when consistent with the full document text
- [X] T027 [US4] Inspect generated prompt text from `ocrpolish/services/tagging_service.py` and verify a nested relative filename appears before the full document text

---

## Phase 8: Category Order for LLM Decoding

**Goal**: Present tag categories to the LLM as Categories/Topics first, Entities second, and Tags last.

**Independent Test**: Inspect the prompt text and Pydantic structured response schema and verify the order is `topic_tags`, `entity_tags`, `conceptual_tags`.

### Implementation for Category Order

- [X] T028 Reorder category instructions in `ocrpolish/services/tagging_service.py` to present `topic_tags` before `entity_tags` before `conceptual_tags`
- [X] T029 Reorder structured LLM schema field declarations in `ocrpolish/models/metadata.py` to present `topic_tags` before `entity_tags` before `conceptual_tags`
- [X] T030 Inspect generated prompt text and model field order to verify Categories/Topics, Entities, Tags order
- [X] T031 Tighten `ocrpolish/services/tagging_service.py` prompt wording so `conceptual_tags` strictly exclude entity duplicates, including aliases, translations, acronyms, expanded names, and normalized variants
- [X] T032 Tighten `ocrpolish/services/tagging_service.py` and `ocrpolish/models/metadata.py` wording so `topic_tags` are a mandatory taxonomy classification step and are not skipped for substantive archival text
- [X] T033 Relax `MIN_SUBSTANTIVE_CONCEPTUAL_TAGS` in `ocrpolish/models/metadata.py` from 3 to 1 and update prompt/schema expectations
- [X] T034 Update only the `topic_tags` prompt section in `ocrpolish/services/tagging_service.py` to require multi-label detection of all supported approved taxonomy topics without duplicating the instruction in critical rules
- [X] T035 Rename prompt input label from document excerpt to full document text in `ocrpolish/services/tagging_service.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion and blocks all user stories.
- **User Stories (Phase 3+)**: Depend on Foundational completion.
- **Polish (Phase 6)**: Depends on all selected user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Starts after Foundational; no dependency on US2 or US3.
- **User Story 2 (P2)**: Starts after Foundational; can be implemented after or alongside US1, but final prompt wording must remain coherent with US1.
- **User Story 3 (P3)**: Starts after Foundational; can be implemented after or alongside US1/US2, but must preserve existing topic/conceptual requirements.

### Within Each User Story

- Edit only LLM prompt text in `ocrpolish/services/tagging_service.py`.
- Inspect the generated prompt text for the story contract.
- Do not edit tests or non-prompt code.
- Stop at the checkpoint before moving to lower-priority work if validating incrementally.

### Parallel Opportunities

- T002 and T003 can run in parallel during setup.
- T017 and T018 can run in parallel during polish because they are review tasks over different acceptance dimensions.

---

## Parallel Example: Setup

```text
Task: "T002 [P] Inspect prompt contract requirements in specs/031-prompt-tag-normalization/contracts/tagging-prompt-contract.md"
Task: "T003 [P] Inspect analysis findings in docs/tag_analysis_report.md and COUNTS_v6.csv"
```

## Parallel Example: Polish

```text
Task: "T017 [P] Confirm no test, CLI option, schema, taxonomy, useful-tags, parser, metadata renderer, indexing, or interlinking changes were made by reviewing git diff -- ocrpolish tests"
Task: "T018 [P] Compare prompt text against specs/031-prompt-tag-normalization/contracts/tagging-prompt-contract.md and update only LLM prompt text in ocrpolish/services/tagging_service.py if any required prompt item is missing"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 by changing only LLM prompt text.
3. Inspect generated prompt text for US1 requirements.
4. Stop and validate that repeated entity variants converge in prompt guidance.

### Incremental Delivery

1. Add US1 entity canonicalization prompt text and inspect prompt output.
2. Add US2 conservative OCR recovery prompt text and inspect prompt output.
3. Add US3 preservation guidance for topics/concepts/acronyms and inspect prompt output.
4. Run existing regression commands without modifying non-prompt code.

### Parallel Team Strategy

Because implementation is one prompt surface, one person should own all edits to `ocrpolish/services/tagging_service.py`; others can inspect artifacts and run validation commands in parallel.

## Notes

- Keep implementation LLM-prompt-text-only unless the feature is explicitly re-scoped.
- Do not edit tests, taxonomy, useful-tags, generated metadata category sets, CLI options, parser logic, output migration behavior, or post-processing behavior.
- Schema field declaration order may be adjusted only to match the prompt's LLM decoding order without adding or removing output categories.
- Commit only files relevant to this feature; leave unrelated untracked analysis files untouched unless explicitly requested.
