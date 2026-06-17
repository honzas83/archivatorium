# Tasks: Item Type Metadata

**Input**: Design documents from `/specs/032-item-type-metadata/`

**Prerequisites**: [plan.md](./plan.md), [spec.md](./spec.md), [research.md](./research.md), [data-model.md](./data-model.md), [contracts/metadata-item-type-contract.md](./contracts/metadata-item-type-contract.md), [quickstart.md](./quickstart.md)

**Tests**: Targeted pytest coverage is required by the implementation plan for schema defaults, prompt text, frontmatter ordering, metadata callouts, and XLSX export.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm the current metadata pipeline files and test targets before feature work begins.

- [X] T001 Review existing metadata schema and extraction prompt behavior in `ocrpolish/models/metadata.py` and `ocrpolish/processor_metadata.py`
- [X] T002 Review current metadata ordering and callout rendering tests in `tests/unit/test_metadata_processor.py`
- [X] T003 [P] Review current XLSX export columns and tests in `ocrpolish/services/indexing_service.py` and `tests/unit/test_xlsx_export.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add shared item-type vocabulary and schema support required by all user stories.

**CRITICAL**: No user story work can begin until this phase is complete.

- [X] T004 Add the approved item-type vocabulary constant and validation type in `ocrpolish/models/metadata.py`
- [X] T005 Add `item_type` with default `other` as the first field on `MetadataSchema` in `ocrpolish/models/metadata.py`
- [X] T006 [P] Add schema tests for default `item_type`, accepted values, and rejected unapproved values in `tests/unit/test_metadata_schema.py`

**Checkpoint**: Foundation ready; metadata extraction has a shared field and closed vocabulary that story work can use.

---

## Phase 3: User Story 1 - Classify Each Item by Document Type (Priority: P1) MVP

**Goal**: Every newly generated metadata record includes `item_type` first, with representative clear document forms classified by the metadata extraction contract.

**Independent Test**: Process representative correspondence, report, agenda, meeting-minutes, directive, and unclear documents, then verify each generated metadata record begins with `item_type` containing one allowed value.

### Tests for User Story 1

- [X] T007 [P] [US1] Add metadata prompt assertions for `item_type`, primary document form, and representative clear types in `tests/unit/test_metadata_processor.py`
- [X] T008 [US1] Add frontmatter ordering assertions that `item_type` is the first rendered key in `tests/unit/test_metadata_processor.py`
- [X] T009 [P] [US1] Add an end-to-end metadata command regression for generated frontmatter containing leading `item_type` in `tests/integration/test_metadata_command.py`

### Implementation for User Story 1

- [X] T010 [US1] Add item-type extraction instructions first in `_build_metadata_prompt`, with representative clear-type examples aligned to the leading structured field in `ocrpolish/processor_metadata.py`
- [X] T011 [US1] Place `item_type` first in the primary metadata ordering inside `_prepare_obsidian_metadata` in `ocrpolish/processor_metadata.py`
- [X] T012 [US1] Ensure generated frontmatter and metadata callout output preserve leading `item_type` through `_render_frontmatter` and `_render_callouts` in `ocrpolish/processor_metadata.py`
- [X] T013 [US1] Run targeted US1 validation for `tests/unit/test_metadata_schema.py`, `tests/unit/test_metadata_processor.py`, and `tests/integration/test_metadata_command.py`

**Checkpoint**: User Story 1 is independently functional and delivers the MVP.

---

## Phase 4: User Story 2 - Use a Closed Type Vocabulary (Priority: P2)

**Goal**: Item-type values are constrained to the approved list across generated metadata and export surfaces, with `other` used for uncertain or unsupported document forms.

**Independent Test**: Review generated outputs for varied document forms and verify every item-type value is exactly one approved value with no synonyms, translated labels, title casing, spaces, or ad hoc variants.

### Tests for User Story 2

- [X] T014 [P] [US2] Add validation tests for synonym, title-case, spaced, and translated item-type rejection in `tests/unit/test_metadata_schema.py`
- [X] T015 [P] [US2] Add XLSX export test coverage for the `Item Type` column and historical missing values in `tests/unit/test_xlsx_export.py`

### Implementation for User Story 2

- [X] T016 [US2] Harden `MetadataSchema.item_type` validation so unapproved non-empty labels fail while missing or empty values resolve to `other` in `ocrpolish/models/metadata.py`
- [X] T017 [US2] Add `Item Type` as a core XLSX metadata column populated from `raw_metadata["item_type"]` in `ocrpolish/services/indexing_service.py`
- [X] T018 [US2] Run targeted US2 validation for `tests/unit/test_metadata_schema.py` and `tests/unit/test_xlsx_export.py`

**Checkpoint**: User Story 2 is independently functional and all generated/exported item-type values are controlled.

---

## Phase 5: User Story 3 - Provide Consistent Classification Guidance (Priority: P3)

**Goal**: The metadata extraction prompt distinguishes adjacent item types consistently using title, headings, opening formula, structure, stated purpose, and content.

**Independent Test**: Run metadata generation against similar-form samples and verify the selected item type follows documented guidance for agenda, corrigendum, note, working paper, report, and study distinctions.

### Tests for User Story 3

- [X] T019 [P] [US3] Add prompt assertions for leading item-type instruction order, adjacent-type distinctions, and source-evidence signals in `tests/unit/test_metadata_processor.py`
- [X] T020 [US3] Add contract-aligned prompt assertions for all approved item-type definitions in `tests/unit/test_metadata_processor.py`

### Implementation for User Story 3

- [X] T021 [US3] Expand `_build_metadata_prompt` with classification guidance for all approved item-type values in `ocrpolish/processor_metadata.py`
- [X] T022 [US3] Add prompt guidance to prefer primary document form over attachments, appendices, quoted material, and incidental references in `ocrpolish/processor_metadata.py`
- [X] T023 [US3] Run targeted US3 validation for `tests/unit/test_metadata_processor.py`

**Checkpoint**: User Story 3 is independently functional and classification guidance covers adjacent forms.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup across all stories.

- [X] T024 [P] Update quickstart validation notes if implemented behavior differs from planned examples in `specs/032-item-type-metadata/quickstart.md`
- [X] T025 Run the targeted feature test suite from quickstart in `tests/unit/test_metadata_schema.py`, `tests/unit/test_metadata_processor.py`, and `tests/unit/test_xlsx_export.py`
- [X] T026 Run broader regression validation for metadata-related tests in `tests/unit/test_metadata_schema.py`, `tests/unit/test_metadata_processor.py`, `tests/unit/test_xlsx_export.py`, and `tests/integration/test_metadata_command.py`
- [X] T027 Run constitution quality gates for changed files `ocrpolish/models/metadata.py`, `ocrpolish/processor_metadata.py`, `ocrpolish/services/indexing_service.py`, `ocrpolish/utils/metadata.py`, `tests/unit/test_metadata_schema.py`, `tests/unit/test_metadata_processor.py`, and `tests/unit/test_xlsx_export.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies; can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion; blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Foundational and is the MVP.
- **User Story 2 (Phase 4)**: Depends on Foundational and can proceed after or alongside US1 once the shared schema field exists.
- **User Story 3 (Phase 5)**: Depends on Foundational and can proceed after or alongside US1/US2 because it only expands prompt guidance.
- **Polish (Phase 6)**: Depends on all selected user stories being complete.

### User Story Dependencies

- **US1 (P1)**: Requires foundational `item_type` schema support; no dependency on US2 or US3.
- **US2 (P2)**: Requires foundational vocabulary; no dependency on US1 output rendering, but export validation is more useful after US1 is complete.
- **US3 (P3)**: Requires foundational vocabulary; can be implemented independently as prompt guidance.

### Parallel Opportunities

- T003 can run in parallel with T001 and T002.
- T006 can run in parallel after T004/T005 choices are clear because it touches only `tests/unit/test_metadata_schema.py`.
- T007 and T009 can be prepared in parallel for US1 because they cover different files and test scopes; coordinate T008 because it shares `tests/unit/test_metadata_processor.py` with T007.
- T014 and T015 can be prepared in parallel for US2 because they touch different test files.
- T019 can be prepared independently for US3; coordinate T020 because it shares `tests/unit/test_metadata_processor.py`.
- US2 and US3 can proceed in parallel after Phase 2 if separate developers coordinate changes to `ocrpolish/processor_metadata.py`.

---

## Parallel Examples

### User Story 1

```text
Task: "Add metadata prompt assertions for item_type, primary document form, and representative clear types in tests/unit/test_metadata_processor.py"
Task: "Add an end-to-end metadata command regression for generated frontmatter containing leading item_type in tests/integration/test_metadata_command.py"
```

### User Story 2

```text
Task: "Add validation tests for synonym, title-case, spaced, and translated item-type rejection in tests/unit/test_metadata_schema.py"
Task: "Add XLSX export test coverage for the Item Type column and historical missing values in tests/unit/test_xlsx_export.py"
```

### User Story 3

```text
Task: "Add prompt assertions for adjacent-type distinctions and source-evidence signals in tests/unit/test_metadata_processor.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 setup review.
2. Complete Phase 2 shared schema and vocabulary support.
3. Complete Phase 3 so generated metadata includes `item_type` first.
4. Validate US1 independently with targeted schema, processor, and metadata command tests.

### Incremental Delivery

1. Deliver US1 to make the field visible and useful in generated metadata.
2. Deliver US2 to harden vocabulary control and export support.
3. Deliver US3 to improve LLM consistency across adjacent document forms.
4. Run polish and quality gates after the selected story set is complete.

### Atomic Git Guidance

- Commit only files relevant to each completed task or logical task group.
- Do not stage unrelated untracked analysis files in the repository root.
- Keep documentation-only task output separate from implementation task output when practical.

---

## Notes

- `[P]` tasks are parallelizable only when assigned with coordination for shared files.
- `[US1]`, `[US2]`, and `[US3]` labels map directly to the prioritized user stories in [spec.md](./spec.md).
- Every implementation task includes an exact target file path.
- Tests are included because the implementation plan explicitly calls for targeted pytest coverage.
