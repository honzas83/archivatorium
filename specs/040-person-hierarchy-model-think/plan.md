# Implementation Plan: Hierarchical Person Entities and Model Reasoning Control

**Branch**: `040-person-hierarchy-model-think` | **Date**: 2026-09-02 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/040-person-hierarchy-model-think/spec.md`

## Summary

Change newly generated Person tags from a combined name to a surname-first path with an optional
given-name or compacted-initials component, while preserving that hierarchy through parsing,
aggregation, export, and surname-grouped indexing. Add a case-insensitive `--model-think` option to
the OCR and metadata commands, default it to `medium`, map `False` to an explicit disabled boolean,
and propagate it only to the Qwen 3.8 OCR request and the primary/follow-up metadata extraction
requests identified by the feature. Existing archive files are not migrated.

## Technical Context

**Language/Version**: Python 3.12 (`requires-python = ">=3.12"`)

**Primary Dependencies**: Click CLI, Pydantic models, Ollama client integration, existing tag
normalization and indexing services

**Storage**: Filesystem Markdown/PDF vault output and generated XLSX metadata index; no storage
format or migration mechanism is added

**Testing**: pytest/pytest-cov, coverage, ruff, flake8 with cognitive-complexity checks, mypy

**Target Platform**: macOS and Linux command-line environments with a configured Ollama service

**Project Type**: Single Python CLI application

**Performance Goals**: Add no model calls; keep entity normalization linear in the number and length
of generated entity paths; reject invalid CLI values before scanning input documents

**Constraints**: Preserve recursive processing, existing model/prompt/output settings outside the
explicitly governed calls, private-reasoning stripping, and old archive files; retain user-owned
working-tree changes; do not add automatic Person-path migration

**Scale/Scope**: Two CLI commands, one OCR request profile, two metadata extraction call sites, the
Person generation/parsing/index pipeline, focused unit/integration tests, and user documentation

## Constitution Check

*GATE: Passed before Phase 0 research and re-checked after Phase 1 design.*

- **I. Quality-Driven Python Development — PASS**: The design remains Python 3.12 and includes
  ruff, formatting, flake8 complexity, mypy, pytest, and coverage gates. Unit tests cover parsing and
  value conversion; integration tests cover CLI propagation and archive consumers.
- **II. CLI-First Interface — PASS**: Both capabilities are exposed through the existing metadata
  workflow and POSIX-style `--model-think` options on the `metadata` and `ocr` commands.
- **III. Recursive Directory Processing — PASS**: Existing recursive discovery and mirrored output
  behavior are unchanged.
- **IV. Data Isolation — PASS**: Committed tests use synthetic names and mocked model responses. Any
  real validation inputs remain under gitignored `data/040-person-hierarchy-model-think/`.
- **V. Atomic Git Workflow — PASS**: Implementation tasks must stage only their named feature paths.
  Existing modified tests and untracked archive datasets are explicitly outside feature commits.
- **Post-design re-check — PASS**: The data model, contracts, and quickstart add no alternate
  language, interface, storage, or data-location mechanism and preserve all required quality gates.

## Project Structure

### Documentation (this feature)

```text
specs/040-person-hierarchy-model-think/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── model-think-cli.md
│   └── person-entity-path.md
├── checklists/
│   └── requirements.md
└── tasks.md                         # Created later by /speckit-tasks
```

### Source Code (repository root)

```text
archivatorium/
├── cli.py                           # Parse and propagate --model-think on both commands
├── ocr_engine.py                    # Qwen 3.8 default and per-run reasoning override
├── processor_metadata.py            # Metadata reasoning state and both extraction calls
├── models/
│   └── metadata.py                  # Model-visible Person path contract
├── services/
│   ├── tagging_service.py           # Person prompt, normalization, and aggregation
│   ├── indexing_service.py          # Surname-based People index grouping
│   └── ollama_client.py             # Existing kwargs forwarding; compatibility verification
└── utils/
    ├── person_entities.py            # Shared Person path normalization and validation
    └── tag_parser.py                 # Accept and preserve one/two-part Person identities

tests/
├── integration/
│   ├── test_cli.py                   # Metadata option acceptance and propagation
│   ├── test_metadata_command.py      # Metadata extraction reasoning behavior
│   ├── test_ocr_cli.py               # OCR option propagation and unaffected profiles
│   └── test_tagging_pass.py          # Generated Person path through metadata output
└── unit/
    ├── test_indexing_service.py      # Surname ordering/grouping
    ├── test_markdown_indices.py      # Full People index paths
    ├── test_metadata_processor.py    # Primary and fallback model calls
    ├── test_ocr_engine.py            # Qwen default/override request values
    ├── test_person_entities.py       # Canonical names, initials, roles, invalid paths
    ├── test_tag_parser.py            # Surname-only and full Person paths
    ├── test_tag_validation.py        # Accepted/rejected Person depths
    └── test_tagging_service.py       # Prompt and generated-entity normalization

README.md                             # Person format and --model-think examples
data/040-person-hierarchy-model-think/ # Optional local-only reviewed validation material
```

**Structure Decision**: Keep the existing single-project CLI layout. Put shared structural Person
normalization in a small utility used by generation and parsing, keep semantic name interpretation in
the tagging prompt, and specialize People-index display/grouping at the existing indexing boundary.
Reasoning choices travel as typed run configuration; the existing Ollama wrappers continue to send
the final request.

## Implementation Design

### Person generation and normalization

- Update model-visible entity descriptions and tagging instructions to request
  `Person/<surname>[/<given-name-or-initials>]`, provide full-name, initials, surname-only, and
  role-exclusion examples, and forbid titles/offices as name components.
- Normalize every generated Person candidate through one shared function before deduplication.
  Require a non-empty surname, permit at most one optional given-name component, normalize each
  component with the existing tag rules, and compact a component consisting solely of initials to
  uppercase letters without separators.
- Reject candidates with missing surnames, surplus hierarchy levels, or components consisting of
  prohibited role/title terms. Semantic surname/given-name interpretation remains the model's job;
  structural validation prevents malformed output from entering the archive.
- Do not reinterpret or rewrite old Markdown. Existing combined paths remain existing text until a
  metadata rerun generates the new format.

### Downstream Person handling

- Extend the canonical Markdown parser to accept `Entities/Person/<surname>` and
  `Entities/Person/<surname>/<given-name-or-initials>`, applying the shared normalization and storing
  the counter value as `surname` or `surname/given`.
- Preserve the complete normalized raw path for Markdown sections and XLSX export. Existing raw-path
  prefix filtering already supports either depth.
- Generate the People index in surname-first order and derive alphabetic headings from the surname
  component rather than the final component. Keep full paths distinct for people sharing a surname.
- Reuse-hint counters retain the complete relative Person identity so later tagging windows receive
  the canonical surname-first form.

### Model reasoning option

- Define one typed conversion for case-insensitive CLI values `False`, `low`, `medium`, and `high`.
  Convert false to boolean `False`; retain the three effort levels as strings. Click rejects all
  other values before command execution.
- Add the option to both commands with `medium` as the visible/default value.
- Set the Qwen 3.8 OCR profile default to `medium` and allow `OCREngine` to receive the converted
  value as a request override for that profile. Standard, GLM, and FireRed retain their current
  profile reasoning behavior even when the shared OCR CLI option has its default value.
- Store the converted value on `MetadataProcessor` and pass it to the primary structured metadata
  extraction and conditional final-date extraction. Do not apply it to `TaggingService`, whose
  extraction remains explicitly non-thinking and is not one of the user-identified call sites.
- Continue using existing response normalization so reasoning text is never written to OCR output.

### Validation strategy

- Unit-test Person normalization independently, including `K-W` and `K. W.` to `KW`, full names,
  surname-only names, compound names, role modifiers, missing surname, and excessive path depth.
- Test the Markdown parser, counters, entity sections, XLSX raw paths, and People index with both
  valid Person depths and shared surnames.
- Test CLI help/defaults/accepted values/invalid values and inspect mocked Ollama calls for correctly
  typed reasoning values. Cover metadata fallback date extraction and each OCR profile boundary.
- Run focused tests first, then the full constitution quality suite. Work around—not overwrite or
  commit—unrelated pre-existing modifications in overlapping test files.

## Complexity Tracking

No constitution violations require justification.
