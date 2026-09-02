# Research: Controlled Tag Evolution

## Decision: Use prompting for semantics and deterministic code for boundaries

**Rationale**: Substantive relevance, synonymy, and whether a compound phrase is a genuine archival
concept require document understanding and belong in the existing LLM call. Numeric limits, exact
normalization, uniqueness, and entity separation are deterministic invariants and must not depend on
model compliance.

**Alternatives considered**:

- Make `USEFUL_TAGS.yaml` an allowlist: rejected because it removes intentional vocabulary
  evolution.
- Detect all semantic redundancy in code: rejected because lexical heuristics would merge distinct
  historical concepts and still miss paraphrases.
- Add a second ranking/validation model call: rejected because the feature requires zero additional
  inference calls.

## Decision: Preserve model importance order and finalize once per document

**Rationale**: The prompt can require descending importance, allowing stable truncation without a
second call. Single-pass and windowed paths should converge on one finalizer. Windowed candidates
remain frequency-ranked, with best local model rank and then first observation breaking ties, before
the shared finalizer applies document-level limits.

**Alternatives considered**:

- Alphabetical truncation: rejected because it discards relevance order.
- Per-window hard quotas: rejected because overlapping windows could exceed document limits and
  waste the novelty budget on repeated local candidates.
- Pydantic maximum lengths: rejected as the only enforcement because validation failure may retry or
  fail instead of retaining the strongest valid subset.

## Decision: Compare normalized exact keys while preserving the first display form

**Rationale**: `normalize_tag_component()` already produces Obsidian-safe canonical paths.
Case-folding that result provides a stable exact comparison key for hash, punctuation, whitespace,
hyphen, and case variants. A first-wins scan preserves the model's importance order and canonical
output without inventing semantic equivalence.

**Alternatives considered**:

- Raw-string equality: rejected because superficial spellings would bypass uniqueness and novelty
  budgets.
- Fuzzy matching or embeddings: rejected because they add complexity, may collapse valid concepts,
  and are unnecessary for the specified exact-deduplication guarantee.

## Decision: Entity collision examines every meaningful path component

**Rationale**: Current suppression compares only the final entity component and lets protected seed
or reused tags bypass collisions. Hierarchical names such as `Person/Luns/Joseph-M-A-H` require both
identity components to be unavailable as conceptual tags. Entity precedence applies regardless of
vocabulary origin.

**Alternatives considered**:

- Compare only complete entity paths: rejected because conceptual output does not include the
  `Entity/type` hierarchy.
- Preserve protected tags on collision: rejected because it reproduces `NATO`, `NPG`, city, and
  person duplication.
- Deterministically infer aliases/translations: rejected as semantic work better handled by the
  prompt; code guarantees normalized exact component separation.

## Decision: Promote after two document occurrences using existing counters

**Rationale**: The archive preflight scan already parses each output file into canonical tag sets and
increments counters once per tag per document. Incremental ingestion updates the same counters after
new output. A monotonic established-tag set populated when counts reach two implements
independent-document promotion without a database or migration and prevents overwrite subtraction
from causing run-time demotion.

**Alternatives considered**:

- Feed every previously generated tag back immediately: rejected because one hallucination can
  amplify across the archive.
- Maintain a persistent vocabulary registry: rejected because existing output documents already
  provide the necessary evidence and the user will rerun metadata.
- Require more than two documents: rejected because the specification establishes two as the
  promotion threshold.

## Decision: Snapshot known vocabulary per document

**Rationale**: Novelty is evaluated against the seed plus established hints available when the
document begins. All windows share that snapshot. Generated tags update counters only after the
document output is assembled, so recurrence in multiple windows cannot count as independent
documents.

**Alternatives considered**:

- Update establishment after every window: rejected because windows are not independent documents.
- Treat all counter entries as established: rejected because it makes the two-document threshold
  ineffective.

## Decision: Reuse the existing typed reasoning option

**Rationale**: The metadata CLI already converts case-insensitive values to `False | "low" |
"medium" | "high"`, defaults to `medium`, and passes them to metadata extraction. `TaggingService`
has a single model-call boundary used once or per window, so constructor injection changes request
configuration without changing call count.

**Alternatives considered**:

- Add a separate tag-reasoning option: rejected because the requirement is one consistent setting
  for the metadata run.
- Keep tag inference hard-coded to `False`: rejected because it prevents model-specific tuning and
  contradicts the command contract.

## Decision: Keep the response and archive schemas unchanged

**Rationale**: The requested result remains a conceptual `list[str]`. Novelty is computed from
existing seed/hint state, so source phrases, justifications, alternative deliberation, and flags are
not needed.

**Alternatives considered**:

- Structured provenance in the same model call: explicitly excluded by the user.
- Persist novelty/establishment flags in Markdown: rejected because it changes the archive format
  and creates migration requirements.
