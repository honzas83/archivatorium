# Implementation Plan: 028-zotero-citation-import

**Branch**: `028-zotero-citation-import` | **Date**: 2026-06-09 | **Spec**: [spec.md](spec.md)

## Summary

The feature adds support for generating Zotero-compatible citation metadata directly into Obsidian Citation callouts. It generates an HTML COinS (ContextObjects in Spans) tag to allow browser extensions like Zotero Connector to instantly detect and save the document when viewing it as HTML. The COinS span uses the generic `mtx:dc` format and `"type": "document"`.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: `json`, `urllib.parse` (stdlib)

**Storage**: Local filesystem

**Testing**: `pytest`, `coverage`

**Target Platform**: CLI

**Project Type**: CLI tool

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] I. Quality-Driven Python Development: Uses Python 3.12.
- [x] II. CLI-First Interface: Integrated directly into the metadata processing step.
- [x] III. Recursive Directory Processing: Maintained via existing CLI commands.
- [x] IV. Data Isolation: Excluded from version control.
- [x] V. Atomic Git Workflow: Will be followed during implementation.

## Project Structure

### Documentation (this feature)

```text
specs/028-zotero-citation-import/
├── plan.md              
├── spec.md        
├── quickstart.md        
└── tasks.md             
```

### Source Code (repository root)

```text
src/
tests/
```

**Structure Decision**: The Zotero parsing logic is added to the metadata utils module in `ocrpolish/utils/metadata.py`.
