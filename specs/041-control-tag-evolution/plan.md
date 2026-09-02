# Implementation Plan: Controlled Tag Evolution

**Branch**: `041-control-tag-evolution` | **Date**: 2026-09-02 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/041-control-tag-evolution/spec.md`

## Summary

Reduce conceptual-tag overproduction while preserving LLM-driven vocabulary growth. Strengthen the
existing tagging prompt so the model selects a small, importance-ranked set of substantive concepts,
then enforce deterministic document-level normalization, entity separation, exact deduplication,
and limits of 20 total and five novel conceptual tags. Continue treating `USEFUL_TAGS.yaml` as a
seed, but expose model-discovered tags as preferred vocabulary only after they occur in two
independent archive documents. Propagate the metadata command's existing typed `--model-think`
value to every tag-inference window without adding model calls or structured tag provenance.

## Technical Context

**Language/Version**: Python 3.12 (`requires-python = ">=3.12"`)

**Primary Dependencies**: Click CLI, Pydantic tagging models, PyYAML seed/taxonomy loading, Ollama
client integration, existing canonical tag parser and sliding-window service

**Storage**: Filesystem Markdown/PDF vault output and in-memory per-document counters populated by
the existing archive scan; no database, registry, migration, or output-schema change

**Testing**: pytest/pytest-cov, coverage, ruff, flake8 with cognitive-complexity checks, mypy

**Target Platform**: macOS and Linux command-line environments with a configured Ollama service

**Project Type**: Single Python CLI application

**Performance Goals**: Add zero inference calls; keep final tag filtering linear in the number and
length of candidate tags and entity-path components; reuse the existing one-pass archive scan

**Constraints**: Prompting remains the primary semantic control; deterministic code enforces only
normalization, entity collisions, exact uniqueness, promotion eligibility, and numeric limits;
preserve model-declared importance order; do not rewrite existing documents or collect structured
provenance; retain user-owned working-tree changes

**Scale/Scope**: Metadata command construction, one tagging service, one reuse-hint boundary, shared
normalization/suppression helpers, prompt/schema descriptions, focused unit/integration tests, and
user documentation

## Constitution Check

*GATE: Passed before Phase 0 research and re-checked after Phase 1 design.*

- **I. Quality-Driven Python Development — PASS**: The design remains Python 3.12 and includes
  ruff, formatting, flake8 complexity, mypy, pytest, and coverage gates. Deterministic policy is
  isolated in testable helpers; model behavior is tested with mocked structured responses.
- **II. CLI-First Interface — PASS**: The existing POSIX-style `--model-think` option becomes the
  single command-scoped reasoning control for metadata and tag inference; no secondary interface is
  introduced.
- **III. Recursive Directory Processing — PASS**: Existing recursive discovery, preflight scanning,
  and mirrored output behavior remain unchanged.
- **IV. Data Isolation — PASS**: Committed tests use synthetic Markdown and mocked model responses.
  Any real validation corpus remains under gitignored `data/041-control-tag-evolution/`.
- **V. Atomic Git Workflow — PASS**: Implementation tasks must stage only their named feature paths.
  Existing modified tests and untracked archive datasets are explicitly outside feature commits.
- **Post-design re-check — PASS**: The data model, contracts, and quickstart introduce no alternate
  storage layer, extra model pass, migration path, or non-CLI control and preserve every quality
  gate.

## Project Structure

### Documentation (this feature)

```text
specs/041-control-tag-evolution/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── conceptual-tag-control.md
│   └── tag-inference-reasoning.md
├── checklists/
│   └── requirements.md
└── tasks.md                         # Created later by /speckit-tasks
```

### Source Code (repository root)

```text
archivatorium/
├── cli.py                           # Pass command-scoped reasoning into tagging
├── processor_metadata.py            # Build established-only reuse hints from document counts
├── models/
│   └── metadata.py                  # Model-visible conceptual-tag selection contract
├── services/
│   └── tagging_service.py           # Prompt, reasoning, aggregation, and final tag policy
└── utils/
    └── nlp.py                       # Canonical comparison and entity-collision helpers

tests/
├── integration/
│   ├── test_model_think_cli.py       # Typed option propagation to both metadata boundaries
│   ├── test_tagging_pass.py          # Final controlled tags through generated Markdown
│   └── test_resume_safety.py         # Existing archive counts and rerun behavior
└── unit/
    ├── test_metadata_reasoning.py    # Tag reasoning default and explicit values
    ├── test_nlp_normalization.py     # Exact normalized dedupe and entity components
    ├── test_processor_counters.py    # Two-document promotion and one-document isolation
    ├── test_tag_suppression.py       # Entity precedence including seed/reused tags
    └── test_tagging_service.py       # Prompt rules, budgets, order, and multi-window behavior

README.md                             # Tag evolution, limits, and reasoning semantics
data/041-control-tag-evolution/       # Optional local-only reviewed validation material
```

**Structure Decision**: Keep the existing single-project CLI layout and the current Markdown tag
format. `MetadataProcessor` remains responsible for archive-level document occurrence counts and
constructs reuse hints. `TaggingService` owns model instructions and one shared finalization path for
single-pass and multi-window candidates. Shared NLP helpers provide canonical comparison keys and
entity components without making semantic synonym decisions.

## Implementation Design

### Prompt-first conceptual selection

- Rewrite the conceptual-tag prompt and Pydantic field descriptions to identify
  `USEFUL_TAGS.yaml` and established reuse hints as preferred—not exclusive—vocabulary.
- Ask for principal archival concepts in descending importance, normally 5–12 for a substantive
  document, explicitly allowing fewer or none when the source does not support them.
- Require substantive discussion, prefer an equivalent seed/established form, and prohibit tags
  inferred only from passing mentions, lexical association, synonym expansion, grammatical
  variation, broader/narrower restatements, or Cartesian-product combinations.
- Keep entity extraction ahead of conceptual tags and strengthen the instruction that people,
  organizations, states, cities, and their aliases are entities rather than concepts.
- Keep the structured response unchanged: a simple `list[str]` with no source phrase,
  justification, considered alternative, novelty flag, or other provenance field.

### Deterministic document-level finalization

- Introduce one finalization path used after single-pass extraction and after all sliding-window
  candidates have been aggregated. Apply normalization, low-value filtering, entity/topic
  separation, exact normalized deduplication, novelty budgeting, and total budgeting in that order.
- Derive a case-insensitive, punctuation-normalized comparison key from canonical tag
  normalization, preserve the first canonical display form, and scan candidates in importance
  order. For multi-window results, retain frequency ranking and use each tag's best local model rank,
  then first-observed order, as deterministic tie-breakers before finalization.
- Build the known vocabulary for the current inference from normalized seed tags plus established
  reuse hints. A candidate outside that set is novel. Retain at most the first five valid novel
  candidates and at most 20 valid candidates overall; continue scanning after a surplus novel tag so
  later valid established tags can still fill the total budget, and never fill a quota artificially.
- Build collision keys from every meaningful component of each normalized entity path, not only its
  last segment. Entity collisions always win, including for seed and established tags. Retain topic
  separation under the existing policy while removing the current protection loophole for entity
  names.
- Validate the substantive-result minimum at the model boundary as today, but allow final filtering
  to produce fewer tags when invalid, duplicate, or entity-colliding candidates are removed. Do not
  manufacture replacements or trigger another inference call.

### Promotion without feedback amplification

- Continue using `CanonicalTagParser` and `MetadataProcessor.preflight_scan()` to populate
  conceptual-tag counters from existing output documents. Because each parsed document exposes a
  set of canonical paths, multiple appearances within one document contribute only one occurrence.
- Maintain a normalized, monotonic established-tag set for the archive run. Populate it when
  preflight counts reach two and update it after each successfully ingested generated document;
  never remove an entry during the run even if overwrite subtraction lowers the live counter.
- Change `_build_tagging_reuse_hints()` so non-seed conceptual tags enter preferred vocabulary only
  when established. Send the full established set in deterministic count-descending/name-ascending
  order so every established tag remains available as required; seed tags remain available directly
  from `TaggingService` regardless of archive count.
- Keep current per-output counter ingestion. A first valid novel occurrence is stored locally but is
  absent from the next prompt; after a second independent document is ingested, later documents can
  receive it as established vocabulary. No automatic demotion occurs during the run.
- Classify novelty against the exact seed-plus-established snapshot supplied for the current
  document. This prevents a tag generated in one window from becoming established in another
  window of that same document.
- Do not add persistent lifecycle metadata or rewrite earlier Markdown; rerunning the metadata
  command remains the adoption and regeneration mechanism.

### Model reasoning propagation

- Add `model_think: ModelThink = MODEL_THINK_DEFAULT` to `TaggingService`, store the typed value, and
  use it in the existing `_extract_chunk()` call to `OllamaClient.extract_structured()`.
- Pass the same converted metadata-command option to both `MetadataProcessor` and `TaggingService`,
  and update CLI help to state that the option controls metadata and tag inference.
- A single-pass document still makes one tag call; a windowed document still makes exactly one call
  per existing window. Every retry/window receives the same `False`, `low`, `medium`, or `high`
  value; `False` remains a boolean and the default remains `medium`.

### Validation strategy

- Unit-test prompt language, seed-versus-novel classification, stable normalized deduplication,
  punctuation/case variants, 20-total and five-novel caps, importance preservation, fewer-than-target
  results, empty administrative stubs, and entity-component collisions with no vocabulary bypass.
- Test multi-window overlap and ordering, ensuring limits apply once to the document aggregate and
  no additional calls are made.
- Test archive preflight and incremental ingestion with one occurrence, repeated appearances in one
  document, exactly two independent documents, pre-existing archives, overwrite subtraction, and
  stable established status.
- Parameterize reasoning tests across `False`, `low`, `medium`, and `high`; assert typed values on
  `TaggingService`, default behavior, every window call, and unchanged call counts.
- Run focused tests before the complete constitutional quality suite. Work around—not overwrite or
  commit—unrelated pre-existing modifications in overlapping test files.

## Complexity Tracking

No constitution violations require justification.
