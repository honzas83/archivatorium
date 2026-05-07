# Tasks: Obsidian Vault Interlinking

**Input**: Design documents from `specs/020-obsidian-interlink-vault/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/cli.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Initialize `ocrpolish/services/interlinking_service.py` with `InterlinkingService` class stub
- [ ] T002 Create integration test file `tests/integration/test_interlink_cli.py`
- [ ] T003 Create unit test file `tests/unit/test_interlinking_service.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Implement `VaultDocument` and `ArchiveCodeMap` data structures in `ocrpolish/services/interlinking_service.py`
- [ ] T005 Implement archive code normalization (whitespace removal) in `ocrpolish/services/interlinking_service.py`
- [ ] T006 Implement prefix-boundary matching logic for archive codes in `ocrpolish/services/interlinking_service.py`
- [ ] T007 Implement the first-pass discovery logic to populate `ArchiveCodeMap` from a directory in `ocrpolish/services/interlinking_service.py`
- [ ] T008 [P] Implement link path resolution utility (Full vault path) in `ocrpolish/services/interlinking_service.py`

**Checkpoint**: Foundation ready - the system can now map archive codes to files.

---

## Phase 3: User Story 1 - Metadata Interlinking (Priority: P1) 🎯 MVP

**Goal**: Convert archive code references in the "Metadata" callout table into clickable links.

**Independent Test**: Run `ocrpolish interlink` on a vault where documents have `references` in their Metadata callout and verify they become `[CODE](path/to/file.md)`.

### Tests for User Story 1

- [ ] T009 [P] [US1] Unit test for reference resolution with language fallback in `tests/unit/test_interlinking_service.py`
- [ ] T010 [P] [US1] Unit test for metadata callout table modification in `tests/unit/test_interlinking_service.py`

### Implementation for User Story 1

- [ ] T011 [US1] Implement regex for identifying and extracting the `[!info] Metadata` callout in `ocrpolish/services/interlinking_service.py`
- [ ] T012 [US1] Implement reference resolution logic (Current -> English -> Any) in `InterlinkingService`
- [ ] T013 [US1] Implement idempotency for metadata links (replace existing links instead of nesting) in `ocrpolish/services/interlinking_service.py`
- [ ] T014 [US1] Implement in-place file update logic for the metadata callout in `ocrpolish/services/interlinking_service.py`
- [ ] T015 [US1] Add the `interlink` command to `ocrpolish/cli.py` and integrate it with `InterlinkingService`
- [ ] T016 [US1] Implement silent ignoring of dangling references (FR-011) in `ocrpolish/services/interlinking_service.py`

**Checkpoint**: User Story 1 (MVP) is functional. Vault documents now have clickable metadata references.

---

## Phase 4: User Story 2 - Document Body Interlinking (Priority: P2)

**Goal**: Convert occurrences of archive codes within the text body into clickable links.

**Independent Test**: Verify that archive codes appearing in the text of a document are converted to links while respecting prefix-boundary and longest-match rules.

### Tests for User Story 2

- [ ] T017 [P] [US2] Unit test for longest-match priority in body text in `tests/unit/test_interlinking_service.py`
- [ ] T018 [P] [US2] Unit test for prefix-boundary matching in body text in `tests/unit/test_interlinking_service.py`

### Implementation for User Story 2

- [ ] T019 [US2] Implement body text scanning logic using sorted (by length) known archive codes in `ocrpolish/services/interlinking_service.py`
- [ ] T020 [US2] Implement link replacement for body text with idempotency (no nesting) in `ocrpolish/services/interlinking_service.py`
- [ ] T021 [US2] Ensure link resolution in body uses the same fallback logic as metadata in `ocrpolish/services/interlinking_service.py`

**Checkpoint**: User Story 2 is functional. "Deep" interlinking within the document text is active.

---

## Phase 5: User Story 3 - Language Version Cross-linking (Priority: P2)

**Goal**: Add a `language_versions` row to the Metadata callout linking to the same document in other languages.

**Independent Test**: Verify that documents with multiple language versions show cross-links in the Metadata callout, and solitary documents do not show the field.

### Tests for User Story 3

- [ ] T022 [P] [US3] Unit test for `language_versions` row insertion and conditional omission in `tests/unit/test_interlinking_service.py`

### Implementation for User Story 3

- [ ] T023 [US3] Implement `language_versions` data retrieval from `ArchiveCodeMap` in `InterlinkingService`
- [ ] T024 [US3] Implement logic to insert the `language_versions` row into the Metadata table (FR-008) in `ocrpolish/services/interlinking_service.py`

**Checkpoint**: User Story 3 is functional. Multilingual documents are now cross-linked.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final verification, documentation, and refinement.

- [ ] T025 [P] Add integration test in `tests/integration/test_interlink_cli.py` covering a full vault processing scenario
- [ ] T026 Implement `dry-run` support to log changes without writing in `ocrpolish/cli.py` and `InterlinkingService`
- [ ] T027 [P] Implement `verbose` logging for mapping and matching in `ocrpolish/services/interlinking_service.py`
- [ ] T028 Final code cleanup and `ruff` linting across `ocrpolish/services/interlinking_service.py`
- [ ] T029 Update `GEMINI.md` to include `interlink` in the Tech/Commands sections
- [ ] T030 Validate full implementation against `specs/020-obsidian-interlink-vault/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Can start immediately.
- **Foundational (Phase 2)**: Depends on Setup. Blocks all user stories.
- **User Story 1 (Phase 3)**: Depends on Phase 2.
- **User Story 2 & 3 (Phases 4 & 5)**: Depend on Phase 2. Can be implemented in parallel or after US1.
- **Polish (Phase 6)**: Depends on all user stories.

### Parallel Opportunities

- T002, T003 (Setup)
- T008 (Foundational) can run alongside T004-T007 if interfaces are defined.
- T009, T010 (US1 Tests)
- T017, T018 (US2 Tests)
- T022 (US3 Tests)
- T025, T027 (Polish)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Setup and Foundational phases.
2. Implement US1 (Metadata Interlinking) - this provides the most structured and critical interlinking value.
3. Validate with US1 integration tests.

### Incremental Delivery

1. Foundation -> Mapping capability ready.
2. US1 -> Metadata interlinking ready (MVP).
3. US2 -> Body interlinking ready (Deep interlinking).
4. US3 -> Language cross-linking ready (Multilingual support).
5. Polish -> Final verification.
