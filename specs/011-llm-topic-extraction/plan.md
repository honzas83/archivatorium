# Implementation Plan: LLM Topic Extraction (Integrated)

**Branch**: `011-llm-topic-extraction` | **Date**: 2026-04-29 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/011-llm-topic-extraction/spec.md`

## Summary

Implement a two-step topic extraction process integrated directly into the existing `metadata` command. The process will use Ollama to first identify applicable high-level categories from a YAML-defined hierarchy and then select at most 3 specific topics within those categories. The resulting topics will be formatted as hierarchical tags (`#Category-Name/Topic-Name`) with detailed reasoning and added to the "Abstract" callout section of Obsidian Markdown files.

## Technical Context

**Language/Version**: Python 3.12  
**Primary Dependencies**: `ollama`, `pyyaml`, `click`, `pydantic`, `re` (stdlib)
**Storage**: Filesystem (recursive directory processing of `.md` files)  
**Testing**: pytest, coverage  
**Target Platform**: CLI (cross-platform Python)
**Project Type**: Single project extension
**Performance Goals**: Combined metadata and topic extraction SHOULD complete within 45 seconds per document (due to extra LLM calls).
**Constraints**: 
- Integration MUST be optional; triggered by `--hierarchy-file` in `metadata`.
- Context window for topics: 10kB raw text (no abstract/summary).
- Strict limit: 3 topics per document (enforced in schema).
- Formatting: List for topics (one per line), inline for flat tags.
- No tags in frontmatter property.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Quality-Driven Python Development**: PASS. Using Python 3.12, ruff, mypy, and pytest.
- **II. CLI-First Interface**: PASS. Integrated into `ocrpolish metadata` command.
- **III. Recursive Directory Processing**: PASS. Inherits existing directory mirroring logic.
- **IV. Data Isolation**: PASS. Test data and samples stay in `data/`.
- **V. Atomic Git Workflow**: PASS. Committing in logical increments.

## Project Structure

### Documentation (this feature)

```text
specs/011-llm-topic-extraction/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (generated later)
```

### Source Code (repository root)

```text
ocrpolish/
├── models/
│   ├── metadata.py      # Existing metadata schemas
│   └── topics.py        # NEW: Pydantic schemas (TopicAssignment with reason)
├── services/
│   ├── ollama_client.py # Existing Ollama client
│   └── topics_service.py # NEW: Two-step extraction logic using 10kB raw text
├── utils/
│   └── metadata.py      # Updated for hierarchical tag formatting
├── cli.py               # Updated to add --hierarchy-file to metadata
└── processor_metadata.py # Updated to integrate TopicExtractor and rework callout
```

**Structure Decision**: Single project extension. The `TopicExtractor` service is invoked by `MetadataProcessor` after primary metadata extraction.

## Complexity Tracking

*No violations identified.*
