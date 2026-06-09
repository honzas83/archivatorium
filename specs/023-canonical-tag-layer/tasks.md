# Tasks: Canonical Tag Data Layer

**Input**: Design documents from `/specs/023-canonical-tag-layer/`

**Prerequisites**: [plan.md](file:///Users/honzas/Research.local/ocrpolish/specs/023-canonical-tag-layer/plan.md), [spec.md](file:///Users/honzas/Research.local/ocrpolish/specs/023-canonical-tag-layer/spec.md), [research.md](file:///Users/honzas/Research.local/ocrpolish/specs/023-canonical-tag-layer/research.md), [data-model.md](file:///Users/honzas/Research.local/ocrpolish/specs/023-canonical-tag-layer/data-model.md), [contracts/tags-contract.md](file:///Users/honzas/Research.local/ocrpolish/specs/023-canonical-tag-layer/contracts/tags-contract.md)

**Tests**: Tests are included to satisfy Core Principle I (Quality-Driven Python Development) and ensure regression safety.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create tag parser module at [ocrpolish/utils/tag_parser.py](file:///Users/honzas/Research.local/ocrpolish/ocrpolish/utils/tag_parser.py)
- [x] T002 [P] Verify development tool configuration (ruff, mypy, pytest) is active and running

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core model infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Define `CanonicalTags` structured data model in [ocrpolish/models/metadata.py](file:///Users/honzas/Research.local/ocrpolish/ocrpolish/models/metadata.py)
- [x] T004 Define `CanonicalTagParser` skeleton and basic regex match pattern in [ocrpolish/utils/tag_parser.py](file:///Users/honzas/Research.local/ocrpolish/ocrpolish/utils/tag_parser.py)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Authoritative Tag Parsing (Priority: P1) 🎯 MVP

**Goal**: Parse authoritative prefixes (`#Entities/`, `#Topics/`, `#Tags/`), normalize components, and deduplicate tags. Refactor index pages and XLSX export.

**Independent Test**: Verify that running the parser on a text block containing canonical, legacy, and unprefixed tags extracts only the canonical tags.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T005 [P] [US1] Write unit tests for tag parsing and normalization in [tests/unit/test_tag_parser.py](file:///Users/honzas/Research.local/ocrpolish/tests/unit/test_tag_parser.py)

### Implementation for User Story 1

- [x] T006 [US1] Implement `CanonicalTagParser.parse_text` in [ocrpolish/utils/tag_parser.py](file:///Users/honzas/Research.local/ocrpolish/ocrpolish/utils/tag_parser.py) to match authoritative prefixes using regex
- [x] T007 [US1] Implement normalization logic in `CanonicalTagParser` utilizing `normalize_tag_component` from [ocrpolish/utils/nlp.py](file:///Users/honzas/Research.local/ocrpolish/ocrpolish/utils/nlp.py)
- [x] T008 [US1] Implement tag deduplication and structured model construction in `CanonicalTagParser.parse_text`
- [x] T009 [US1] Refactor `IndexingService.process_file` in [ocrpolish/services/indexing_service.py](file:///Users/honzas/Research.local/ocrpolish/ocrpolish/services/indexing_service.py) to use `CanonicalTagParser` for extracting tags instead of raw string/frontmatter regexes
- [x] T010 [US1] Refactor index page generation (States, Cities, Orgs, Topics) in [ocrpolish/services/indexing_service.py](file:///Users/honzas/Research.local/ocrpolish/ocrpolish/services/indexing_service.py) to consume the structured model (`CanonicalTags`)
- [x] T011 [US1] Refactor XLSX export in [ocrpolish/services/indexing_service.py](file:///Users/honzas/Research.local/ocrpolish/ocrpolish/services/indexing_service.py) to write columns based on the structured model (`conceptual_tags`, `topic_tags`, `state_entities`, `org_entities`, `city_entities`, `person_entities`)
- [x] T012 [US1] Run unit tests via `pytest tests/unit/test_tag_parser.py` and ensure they pass

**Checkpoint**: User Story 1 is fully functional and testable independently.

---

## Phase 4: User Story 2 - Tag-Based Counter Generation (Priority: P1)

**Goal**: Compile tag-based counters independently of frontmatter, and implement preflight scan and skip/overwrite counter updates.

**Independent Test**: Verify state/org/city/person and topic/conceptual tag counters are correctly populated by scanning the output folder and processing skipped/overwritten files.

### Tests for User Story 2

- [x] T013 [P] [US2] Write unit tests for preflight scan and incremental counter updates in [tests/unit/test_processor_counters.py](file:///Users/honzas/Research.local/ocrpolish/tests/unit/test_processor_counters.py)

### Implementation for User Story 2

- [x] T014 [US2] Define structured counters (`conceptual_tag_counts`, `topic_counts`, `entity_counts`) in `MetadataProcessor` in [ocrpolish/processor_metadata.py](file:///Users/honzas/Research.local/ocrpolish/ocrpolish/processor_metadata.py) and remove legacy counts (`tag_counts`, `state_counts`, `org_counts`, `city_counts`)
- [x] T015 [US2] Implement `MetadataProcessor._preflight_scan` in [ocrpolish/processor_metadata.py](file:///Users/honzas/Research.local/ocrpolish/ocrpolish/processor_metadata.py) to scan output directory, parse existing `.md` files, and initialize counters
- [x] T016 [US2] Implement overwrite subtraction logic in `MetadataProcessor.process_file` to remove old tags from counters if a file is re-processed
- [x] T017 [US2] Update `MetadataProcessor.process_file` and [ocrpolish/cli.py](file:///Users/honzas/Research.local/ocrpolish/ocrpolish/cli.py) to populate counters from newly parsed files and update the file tags registry
- [x] T018 [US2] Run unit tests via `pytest tests/unit/test_processor_counters.py` and ensure they pass

**Checkpoint**: User Stories 1 and 2 should both work independently.

---

## Phase 5: User Story 3 - Malformed Tag Detection and Warning (Priority: P2)

**Goal**: Detect, ignore, and log warnings/diagnostics for malformed tags.

**Independent Test**: Verify that malformed tags log warning logs and do not update counters.

### Tests for User Story 3

- [x] T019 [P] [US3] Write unit tests for malformed tag validation and warnings in [tests/unit/test_tag_validation.py](file:///Users/honzas/Research.local/ocrpolish/tests/unit/test_tag_validation.py)

### Implementation for User Story 3

- [x] T020 [US3] Implement validation logic in `CanonicalTagParser` for State, Org, Person (exactly 3 components) and City (exactly 4 components)
- [x] T021 [US3] Implement warning logging in `CanonicalTagParser` for any invalid prefix or malformed structure
- [x] T022 [US3] Ensure malformed tags are excluded from the output structured model and do not update counters
- [x] T023 [US3] Run unit tests via `pytest tests/unit/test_tag_validation.py` and ensure they pass

**Checkpoint**: All user stories are independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T024 [P] Run code formatting checks with `ruff check .` and `ruff format .`
- [x] T025 [P] Run static type analysis with `mypy .`
- [x] T026 Run all tests with coverage (`coverage run -m pytest` and `coverage report`) and ensure test coverage does not decrease
- [x] T027 Validate quickstart code examples from [specs/023-canonical-tag-layer/quickstart.md](file:///Users/honzas/Research.local/ocrpolish/specs/023-canonical-tag-layer/quickstart.md)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories.
- **User Stories (Phase 3+)**: All depend on Foundational phase completion.
  - User Story 1 (P1) is the MVP and must be completed first.
  - User Story 2 (P1) can proceed in parallel or after User Story 1.
  - User Story 3 (P2) depends on User Story 1 parsing logic being defined.
- **Polish (Final Phase)**: Depends on all user stories being complete.

### Parallel Opportunities

- All tasks marked [P] can run in parallel.
- Tests [T005], [T013], and [T019] can be drafted in parallel before implementation.
- Setup [T001] and Foundational [T003], [T004] can be developed independently of the core service refactors.

---

## Parallel Example: User Story 1

```bash
# Launch test drafting and mock setups together:
Task: "Write unit tests for tag parsing and normalization in tests/unit/test_tag_parser.py"

# Implement core parsing logic and file validation:
Task: "Implement CanonicalTagParser.parse_text in ocrpolish/utils/tag_parser.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup.
2. Complete Phase 2: Foundational (blocks all stories).
3. Complete Phase 3: User Story 1.
4. **STOP and VALIDATE**: Test User Story 1 independently.

### Incremental Delivery

1. Complete Setup + Foundational -> Foundation ready.
2. Add User Story 1 -> Test independently -> Deploy/Demo (MVP!).
3. Add User Story 2 -> Test counters & preflight -> Deploy/Demo.
4. Add User Story 3 -> Test malformed validation -> Deploy/Demo.
