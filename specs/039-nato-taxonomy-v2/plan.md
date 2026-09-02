# Implementation Plan: NATO Topic Taxonomy V2

**Branch**: `039-nato-taxonomy-v2` | **Date**: 2026-09-02 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/039-nato-taxonomy-v2/spec.md`

## Summary

Add an explicitly selected, versioned NATO topic taxonomy that separates overloaded nuclear,
governance, command, and infrastructure concepts and applies one universal substantive-subject
threshold. Preserve `topics/NATO_themes.yaml` byte-for-byte. Extend taxonomy preparation so the
classifier receives category context and all topic guidance, validate the taxonomy and model topic
paths strictly. Maintainers adopt v2 by rerunning the existing metadata command with the new taxonomy
into their chosen output directory; there is no path-migration or quotation-verification feature.

## Technical Context

**Language/Version**: Python 3.12 (`requires-python = ">=3.12"`)

**Primary Dependencies**: Click, Pydantic, PyYAML, Ollama client integration

**Storage**: Versioned YAML taxonomy input and filesystem Markdown archive output; local validation
corpora under the gitignored `data/` directory

**Testing**: pytest/pytest-cov, coverage, ruff, flake8 with cognitive-complexity checks, mypy

**Target Platform**: macOS and Linux command-line environments with a configured Ollama service

**Project Type**: Single Python CLI application

**Performance Goals**: Prepare and validate the taxonomy once per CLI run; do not add model requests
per document/window; keep taxonomy and result-path validation linear in taxonomy/result size

**Constraints**: Preserve the v1 taxonomy byte-for-byte and its explicit selection behavior; retain
two-part `Category/Topic` output paths; allow empty topic lists; do not transform existing archives;
do not commit archive feedback or other real documents; preserve unrelated working-tree
changes

**Scale/Scope**: One 55-topic v2 taxonomy in six categories, two classification services, one metadata
model module, focused unit/integration tests, and CLI documentation

## Constitution Check

*GATE: Passed before Phase 0 research and re-checked after Phase 1 design.*

- **I. Quality-Driven Python Development — PASS**: The design uses Python 3.12 and includes ruff,
  flake8, mypy, pytest, and coverage gates. Unit tests isolate taxonomy and topic-path behavior; an
  integration test covers taxonomy selection and tagging behavior.
- **II. CLI-First Interface — PASS**: V2 is selected through the existing required POSIX-style
  `--hierarchy-file` option. No parallel UI or hidden default is introduced.
- **III. Recursive Directory Processing — PASS**: The existing metadata command retains recursive
  input/output behavior. The feature changes classification preparation and validation, not directory
  traversal.
- **IV. Data Isolation — PASS**: Human-reviewed and historical archive cases stay under gitignored
  `data/039-nato-taxonomy-v2/`; committed tests use synthetic text only.
- **V. Atomic Git Workflow — PASS**: Implementation tasks must commit only feature-specific paths.
  Existing unrelated modified and untracked files must not be staged.
- **Post-design re-check — PASS**: The data model, contracts, and quickstart introduce no alternate
  storage, interface, language, or data-location mechanism and retain all quality gates.

## Project Structure

### Documentation (this feature)

```text
specs/039-nato-taxonomy-v2/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── metadata-taxonomy-selection.md
│   └── taxonomy-v2-schema.md
├── checklists/
│   └── requirements.md
└── tasks.md                         # Created later by /speckit-tasks
```

### Source Code (repository root)

```text
archivatorium/
├── cli.py                           # Existing explicit hierarchy selection; verify only
├── models/
│   └── metadata.py                  # Align model-visible topic guidance
└── services/
    ├── flattening_service.py        # Strict validation and complete classifier context
    ├── tagging_service.py           # Policy prompt, complete context, approved paths
    ├── indexing_service.py          # Compatibility verification only
    └── ollama_client.py             # Existing structured extraction; no planned change

topics/
├── NATO_themes.yaml                 # Preserve byte-for-byte
├── NATO_themes_v2.yaml              # New taxonomy and classification policy
└── USEFUL_TAGS.yaml

tests/
├── conftest.py                      # Reusable minimal valid taxonomy fixture if appropriate
├── integration/
│   └── test_tagging_pass.py         # End-to-end classification result filtering
└── unit/
    ├── test_flattening.py            # Schema, context preservation, collision validation
    ├── test_nato_taxonomy_v2.py      # Counts, placement, corrections, v1 integrity
    └── test_tagging_service.py       # Prompt, approved paths, empty topics, window aggregation

README.md                             # Explicit v1/v2 rerun examples
data/039-nato-taxonomy-v2/            # Local-only reviewed validation inputs and reports
```

**Structure Decision**: Keep the existing single-project CLI layout. Taxonomy schema validation
belongs at the current flattening/loading boundary, while candidate-path validation belongs in
`TaggingService` before result aggregation. No new application
layer, database, hierarchy depth, or CLI option is required.

## Implementation Design

### Taxonomy

- Create `topics/NATO_themes_v2.yaml` using the existing `categories -> topics` shape plus
  `schema_version` and a root `classification_policy`.
- Include six exact category names and 55 unique normalized topic paths. Retain all unaffected topic
  meanings; make the required moves, renames, and two splits.
- Do not add path-migration metadata. The supported transition is a fresh metadata run using v2.

### Taxonomy preparation

- Preserve the existing topic-level `description` output key and add `category` and
  `category_description`; retain every non-empty positive and negative example.
- Validate common v1/v2 structure, non-empty path components and descriptions, sample types, and
  duplicate normalized paths. Apply the additional policy/category invariants only to
  `schema_version: 2`.
- Raise a dedicated, actionable taxonomy-validation error for unreadable, invalid, or incomplete
  taxonomy data. Do not convert load failures to an empty taxonomy.
- Serialize the classifier context as a prompt object containing the effective classification policy
  and the complete flattened topic list. Apply the same built-in universal substantive-subject rule
  when a valid legacy taxonomy has no root policy.

### Tagging behavior

- Present the effective universal policy and complete flattened taxonomy in both single-pass and
  sliding-window prompts.
- Align model-visible result descriptions with the substantive-subject rule and explicitly allow an
  empty thematic topic list.
- Normalize each candidate topic path and require membership in the approved flattened-ID set before
  aggregation; drop unsupported paths with an actionable warning.
- Deduplicate supported results by normalized path, retaining the earliest assignment.
- Do not add quotation matching, evidence retry/repair, or additional model calls.

### Validation strategy

- Use synthetic unit cases for deterministic schema, policy, path, and aggregation behavior.
- Use a small synthetic integration case to prove only approved topics cross the tagging
  boundary and an administrative document can retain an empty topic list.
- Run the real NATO feedback corpus only from `data/039-nato-taxonomy-v2/`, producing an untracked
  score report for SC-001 through SC-006. Compare fresh v1/v2 runs and the original v1 checksum
  without rewriting existing archives.

## Complexity Tracking

No constitution violations require justification.
