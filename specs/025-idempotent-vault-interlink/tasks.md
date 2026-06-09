# Tasks: Idempotent Vault Interlinking and Finalization

**Input**: Design documents from `/specs/025-idempotent-vault-interlink/`

**Prerequisites**: [plan.md](plan.md) (required), [spec.md](spec.md) (required), [research.md](research.md), [data-model.md](data-model.md), [contracts/cli.md](contracts/cli.md)

**Tests**: Included as part of the quality gate and validation requirements.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Contains exact file paths in descriptions.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: CLI option registration and service integration.

- [X] T001 Register the unified `interlink` CLI command arguments and options in `ocrpolish/cli.py`
- [X] T002 [P] Configure necessary imports and helpers in `ocrpolish/services/interlinking_service.py` and `ocrpolish/services/indexing_service.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Single-pass scanner and shared memory document record structure.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T003 Implement `VaultDocument` dataclass or class structure in `ocrpolish/services/interlinking_service.py` representing in-memory document record
- [X] T004 Implement single-pass file scanner in `ocrpolish/services/interlinking_service.py` to recursively traverse the vault directory, excluding `Index - *.md`, `metadata_index.xlsx`, `.obsidian/` files, and template directories

**Checkpoint**: Foundation ready - user story implementation can now begin.

---

## Phase 3: User Story 1 - Idempotent Vault Interlinking (Priority: P1) 🎯 MVP

**Goal**: In-place interlinking of files by resolving archive codes, enriching Metadata tables, preventing self-links, and avoiding nested links on repeated runs.

**Independent Test**: Run interlink command twice on mock vault; verify files are linked correctly and subsequent run produces zero diff.

### Tests for User Story 1

- [X] T005 [P] [US1] Create unit/integration tests for idempotent link wrapping and self-linking prevention in `tests/test_interlink_idempotency.py`

### Implementation for User Story 1

- [X] T006 [US1] Refactor `resolve_link` and `normalize_code` in `ocrpolish/services/interlinking_service.py` to prevent nested links and double-wrapping
- [X] T007 [US1] Implement self-linking prevention logic using BibTeX-style key comparisons in `ocrpolish/services/interlinking_service.py`
- [X] T008 [US1] Implement in-place body interlinking and Metadata callout table reference/language version enrichment in `ocrpolish/services/interlinking_service.py`
- [X] T009 [US1] Implement the file reparse/update trigger in `ocrpolish/services/interlinking_service.py` to rebuild in-memory document records if document files were modified during interlinking

**Checkpoint**: At this point, User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 - Markdown Index Generation (Priority: P2)

**Goal**: Generate Index - States/Cities/Organizations/People/Topics/Tags.md using `CanonicalTagParser` from prefix tags.

**Independent Test**: Verify navigation markdown index files are generated under `VAULT_DIR` with alphabetical order and correct groupings.

### Tests for User Story 2

- [X] T010 [P] [US2] Create index validation tests in `tests/test_markdown_indices.py`

### Implementation for User Story 2

- [X] T011 [US2] Implement alphabetical index generator for States, Organizations, People, Topics, and Tags in `ocrpolish/services/indexing_service.py`
- [X] T012 [US2] Implement Cities grouping by parent State in `ocrpolish/services/indexing_service.py`
- [X] T013 [US2] Remove all dependencies on obsolete unprefixed tags (e.g. `#State/` or `#Org/`) in `ocrpolish/services/indexing_service.py`

**Checkpoint**: At this point, User Stories 1 and 2 work together.

---

## Phase 5: User Story 3 - XLSX Metadata Export (Priority: P3)

**Goal**: Export metadata to `metadata_index.xlsx` with core metadata (including stable `citekey` derived from filename stem) and pivoted tag model columns.

**Independent Test**: Verify `metadata_index.xlsx` is generated in `VAULT_DIR` matching the canonical tag parser results.

### Tests for User Story 3

- [X] T014 [P] [US3] Create spreadsheet validation tests in `tests/test_xlsx_export.py`

### Implementation for User Story 3

- [X] T015 [US3] Refactor `generate_xlsx` in `ocrpolish/services/indexing_service.py` using `xlsxwriter` to pivot away from `MetadataSchema` fields and obsolete mentioned columns
- [X] T016 [US3] Implement Excel columns for core metadata (including `citekey`) and pivoted columns for States, Cities, Organizations, People, Topics, and Tags
- [X] T017 [US3] Ensure the Excel generation uses the same `CanonicalTagParser` and counters as the Markdown index generation to ensure consistency

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: End-to-end orchestration, quality gates, and documentation.

- [X] T018 Integrate finalization workflow inside `ocrpolish/cli.py` to orchestrate interlinking, reparsing, indexing, and Excel generation
- [X] T019 Run quality gates: formatting (`ruff format .`), linting (`ruff check .`), type checks (`mypy .`), and test suite (`pytest`)
- [X] T020 Run end-to-end validation scenarios documented in [quickstart.md](quickstart.md)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies.
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) completion. Blocks all user stories.
- **User Stories (Phase 3+)**: All depend on Foundational (Phase 2) completion. They can proceed sequentially in priority order (P1 → P2 → P3).
- **Polish (Phase 6)**: Depends on all user stories being complete.

### Parallel Opportunities

- Setup tasks (T001, T002) can run in parallel.
- User story tests (T005, T010, T014) can be prepared in parallel with design or other tasks.
- Once Foundation (Phase 2) is complete, implementation of US1, US2, and US3 can start or proceed in parallel where there are no code conflicts (e.g. `indexing_service.py` vs `interlinking_service.py`).

---

## Parallel Example: User Story 1

```bash
# Launch test tasks for User Story 1:
Task: "Create unit/integration tests for idempotent link wrapping and self-linking prevention in tests/test_interlink_idempotency.py"

# Implement parallelizable tasks:
Task: "Refactor resolve_link and normalize_code in ocrpolish/services/interlinking_service.py to prevent nested links and double-wrapping"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories).
3. Complete Phase 3: User Story 1 (Interlinking).
4. **STOP and VALIDATE**: Verify idempotency of file modifications.

### Incremental Delivery

1. Foundation ready.
2. Add interlinking (US1) -> Test independently -> Demo (MVP!).
3. Add Markdown indices (US2) -> Test and navigate.
4. Add Excel export (US3) -> Reconcile citekey and pivoted columns.
