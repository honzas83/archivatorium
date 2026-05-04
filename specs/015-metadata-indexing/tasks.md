# Tasks: Metadata Indexing

**Feature**: Metadata Indexing
**Plan**: [plan.md](plan.md)
**Branch**: `015-metadata-indexing`

## Implementation Strategy
We will implement a new `index` subcommand that scans the Obsidian vault, extracts metadata from both YAML frontmatter and `[!abstract]` callouts, and generates various index formats. The core logic will reside in `IndexingService`, while `metadata.py` will be enhanced with abstract parsing capabilities.

## Phase 1: Setup
- [ ] T001 Add `XlsxWriter` dependency to `pyproject.toml`
- [ ] T002 [P] Create `ocrpolish/services/indexing_service.py` with basic class structure
- [ ] T003 Update `ocrpolish/cli.py` to include the `index` subcommand skeleton

## Phase 2: Foundational (Data Extraction)
- [ ] T004 Implement recursive file scanner in `ocrpolish/services/indexing_service.py`
- [ ] T005 [P] Implement `IndexEntry` and `EntityReference` models in `ocrpolish/services/indexing_service.py`
- [ ] T006 [P] Create `extract_abstract_tags` function in `ocrpolish/utils/metadata.py` using regex
- [ ] T007 [P] Implement YAML frontmatter parsing and merging logic in `ocrpolish/services/indexing_service.py`

## Phase 3: [US3] Abstract Callout Integration (P2)
- [ ] T008 [US3] Integrate `extract_abstract_tags` into the document processing flow in `ocrpolish/services/indexing_service.py`
- [ ] T009 [US3] Implement entity deduplication logic (frontmatter vs abstract) in `ocrpolish/services/indexing_service.py`

## Phase 4: [US1] XLSX Metadata Index (P1)
- [ ] T010 [US1] Implement XLSX workbook initialization and header generation in `ocrpolish/services/indexing_service.py`
- [ ] T011 [US1] Implement row-by-row metadata export based on `MetadataSchema` in `ocrpolish/services/indexing_service.py`
- [ ] T012 [US1] Connect `--output-xlsx` CLI option to the indexing service in `ocrpolish/cli.py`

## Phase 5: [US2] Obsidian Index Pages (P1)
- [ ] T013 [US2] Implement `Index - States.md` generation with A-Z grouping in `ocrpolish/services/indexing_service.py`
- [ ] T014 [US2] Implement `Index - Cities.md` generation with State-based grouping in `ocrpolish/services/indexing_service.py`
- [ ] T015 [US2] Implement `Index - Organizations.md` generation in `ocrpolish/services/indexing_service.py`
- [ ] T016 [US2] Implement YAML topics parser for hierarchical descriptions in `ocrpolish/services/indexing_service.py`
- [ ] T017 [US2] Implement `Index - Topics.md` generation using hierarchical hashtags in `ocrpolish/services/indexing_service.py`
- [ ] T018 [US2] Connect `--topics-yaml` CLI option to the indexing service in `ocrpolish/cli.py`

## Phase 6: Polish & Cross-Cutting
- [ ] T019 [P] Implement graceful error handling for malformed markdown or YAML in `ocrpolish/services/indexing_service.py`
- [ ] T020 Add progress bar support for the `index` subcommand in `ocrpolish/cli.py`
- [ ] T021 [P] Ensure all generated indices follow the hashtag-only linking convention in `ocrpolish/services/indexing_service.py`
- [ ] T022 Verify performance criteria (SC-002) by measuring execution time for a large vault
- [ ] T023 Manually verify generated index pages in Obsidian for rendering and link compatibility (SC-004)
- [ ] T024 Run all quality gates: `ruff check .`, `mypy .`, and `pytest` (Constitution Principle I)
- [ ] T025 [P] Handle invalid UTF-8 encoding when reading markdown files in `ocrpolish/services/indexing_service.py`

## Dependencies
1. T004-T007 are prerequisites for all User Stories.
2. US3 (T008-T009) should be completed before US1/US2 for complete entity coverage, despite lower priority.
3. US1 and US2 are independent and can be implemented in parallel.

## Parallel Execution Examples
- T002, T003, T005, T006 can be worked on concurrently.
- T010-T011 (US1) and T013-T015 (US2) can be worked on concurrently after Phase 2/3.
- T019, T021, T023, and T025 can be addressed at any time during Polish phase.
