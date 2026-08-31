# Tasks: Escape Non-Standard Hashtags in Vault

**Input**: Design documents from `/specs/034-escape-other-hashtags/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md

**Tests**: pytest and pytest-cov configured and passing on unit tests.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Paths assume single project structure with `archivatorium/` and `tests/` at repository root.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure verification

- [X] T001 Verify pytest configuration in pyproject.toml

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core function signatures and structure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 Implement escape_other_hashtags function shell in archivatorium/services/interlinking_service.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Escape non-standard hashtags during interlinking (Priority: P1) 🎯 MVP

**Goal**: Escape any raw hashtag in document bodies that is not a canonical tag or a markdown header.

**Independent Test**: Run interlink command on a mock vault containing `#67-87155` and `#Entities/Org/NATO`, verify `#67-87155` becomes `\#67-87155` while `#Entities/Org/NATO` remains untouched.

### Tests for User Story 1
- [X] T003 [P] [US1] Create unit tests for regex hashtag escaping in tests/unit/test_interlinking_service.py

### Implementation for User Story 1
- [X] T004 [US1] Implement escape_other_hashtags regex replacement in archivatorium/services/interlinking_service.py
- [X] T005 [US1] Integrate escape_other_hashtags into _interlink_single_doc in archivatorium/services/interlinking_service.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Idempotency and safe escaping (Priority: P2)

**Goal**: Ensure running the interlink command repeatedly does not double-escape hashes, and does not alter headers, code blocks, or YAML frontmatter.

**Independent Test**: Run the interlink command twice on the same document and verify no extra changes are introduced.

### Tests for User Story 2
- [X] T006 [P] [US2] Add idempotency and safety tests in tests/unit/test_interlinking_service.py

### Implementation for User Story 2
- [X] T007 [US2] Verify header, code block, and frontmatter boundaries in archivatorium/services/interlinking_service.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Capped index pages with Obsidian search links (Priority: P3)

**Goal**: Limit inline links in tag/entity index pages to 50, appending remaining count and an Obsidian Search link.

**Independent Test**: Generate a tag index with >50 matching documents, verify that exactly 50 links are listed, followed by an Obsidian search URL.

### Tests for User Story 3
- [X] T008 [P] [US3] Add unit tests for index capping in tests/unit/test_indexing_service.py

### Implementation for User Story 3
- [X] T009 [US3] Implement capped tag indexing in _gen_alphabetical_index in archivatorium/services/indexing_service.py
- [X] T010 [US3] Implement capped city indexing in _gen_cities_index in archivatorium/services/indexing_service.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Code quality, test coverage, and end-to-end validation verification

- [X] T011 Run all unit tests with coverage in tests/
- [X] T012 Run code formatting and type checks on the workspace
- [X] T013 Run validation scenario in specs/034-escape-other-hashtags/quickstart.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
- **Polish (Final Phase)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2)
- **User Story 2 (P2)**: Can start after US1 is implemented
- **User Story 3 (P3)**: Can start after Foundational (Phase 2)

### Parallel Opportunities

- T003 [P] [US1] and T008 [P] [US3] can run in parallel.
- Development of US3 can run in parallel with US1/US2.

---

## Parallel Example: User Stories

```bash
# Launch model/logic tests for US1 and US3 together:
pytest tests/unit/test_interlinking_service.py
pytest tests/unit/test_indexing_service.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
