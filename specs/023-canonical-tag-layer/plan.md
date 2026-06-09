# Implementation Plan: Canonical Tag Data Layer

**Branch**: `023-canonical-tag-layer` | **Date**: 2026-06-09 | **Spec**: [spec.md](file:///Users/honzas/Research.local/ocrpolish/specs/023-canonical-tag-layer/spec.md)

**Input**: Feature specification from `/specs/023-canonical-tag-layer/spec.md`

## Summary

The goal of this feature is to establish a canonical tag parsing and storage layer for OCRPolish. Currently, tags and entities are parsed in an ad-hoc manner from frontmatter and abstract callout strings, which leads to inconsistent normalization, duplicate values, and tight coupling with the frontmatter metadata schema. 

We will introduce:
1. A structured data model `CanonicalTags` representing parsed conceptual tags, grouped entities (State, Org, City, Person), and topics.
2. A robust `CanonicalTagParser` that parses generated Markdown text, normalizes tags consistently using existing components, validates structures (e.g. City tags must have 3 parts: `City/<State>/<City>`), and filters out legacy/obsolete tags with warning diagnostics.
3. Clean refactoring of the resume preflight scan, indexing service, XLSX exporter, and metadata counters to consume this new canonical tag model instead of raw strings.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: click, pydantic, pyyaml, xlsxwriter (Python standard library: pathlib, typing, collections, re)

**Storage**: Local filesystem (Markdown files, Consolidated frequency.txt, sidecar frequency.txt, index.xlsx)

**Testing**: pytest (with coverage)

**Target Platform**: macOS (POSIX CLI environment)

**Project Type**: CLI utility / parser library

**Performance Goals**: Tag parsing of a single Markdown file must take < 5ms. Memory usage for preflight scan of a large vault (1000+ files) must be < 50MB.

**Constraints**:
- Obsidian tag syntax compatibility (no spaces, kebab-case components, forward slash hierarchy).
- Decoupled from YAML frontmatter fields (all tag-based counters derived solely from parsed hashtags in body/abstract).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Development is in Python 3.12 (Principle I)
- [x] Code quality checks (ruff, mypy, pytest) will be run and pass (Principle I)
- [x] CLI compatibility is maintained (Principle II)
- [x] Recursive directory structure support is preserved (Principle III)
- [x] Local test data is isolated/ignored (Principle IV)
- [x] Atomic git workflow commits will be performed (Principle V)

## Project Structure

### Documentation (this feature)

```text
specs/023-canonical-tag-layer/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (contracts)
│   └── tags-contract.md # Tag format contract
└── checklists/
    └── requirements.md  # Specification quality checklist
```

### Source Code (repository root)

```text
ocrpolish/
├── __init__.py
├── cli.py               # CLI command group and arguments
├── core.py              # Cleaning and paragraph wrapping
├── data_model.py        # Shared data structures and constants
├── processor_metadata.py# Metadata extraction processor & preflight scan
├── models/
│   ├── __init__.py
│   ├── metadata.py      # Schema/structured models
│   └── topics.py
├── services/
│   ├── __init__.py
│   ├── indexing_service.py# Index and XLSX generation
│   ├── tagging_service.py  # Precision tagging LLM pass
│   └── interlinking_service.py
└── utils/
    ├── __init__.py
    ├── docx_utils.py
    ├── files.py
    ├── logging.py
    ├── metadata.py      # Frontmatter & callout helpers
    ├── nlp.py           # Text/tag normalization helpers
    └── tag_parser.py    # [New] Canonical tag parser
```

**Structure Decision**: Single project layout matching existing codebase. We will introduce `ocrpolish/utils/tag_parser.py` and modify `ocrpolish/processor_metadata.py` and `ocrpolish/services/indexing_service.py` to consume the new model.

## Complexity Tracking

*No violations identified.*
