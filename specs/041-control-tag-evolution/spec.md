# Feature Specification: Controlled Tag Evolution

**Feature Branch**: `041-control-tag-evolution`

**Created**: 2026-09-02

**Status**: Draft

**Input**: User description: "Control conceptual-tag overuse while keeping USEFUL_TAGS.yaml as a seed rather than an allowlist. Preserve LLM-driven tag-list evolution, use prompting as the primary control with hard limits enforced by the application, and apply --model-think to tag inference. Do not add structured provenance for novel tags."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate a Focused, Evolving Tag Set (Priority: P1)

As an archive researcher, I want the language model to select a compact set of substantive
conceptual tags while remaining free to introduce genuinely useful new vocabulary, so that document
discovery improves without producing speculative families of loosely related tags.

**Why this priority**: Excessive and combinatorial tags reduce precision, obscure the important
subjects, and pollute later processing. At the same time, freezing the vocabulary would remove a key
feature of the archive workflow.

**Independent Test**: Process synthetic model output containing supported tags, duplicate spellings,
entity names, and a large combinatorial tag family. Verify that the final result retains useful seed,
established, and novel concepts while removing invalid entries and respecting both hard limits.

**Acceptance Scenarios**:

1. **Given** a document substantively discussing seven distinct concepts, **when** tag inference is
   performed, **then** the resulting conceptual tags are concise, non-duplicative, and ordered by
   importance.
2. **Given** a document that supports a useful concept absent from the seed vocabulary, **when** the
   model proposes that concept, **then** it may appear as a novel conceptual tag in that document.
3. **Given** model output containing more than 20 conceptual tags, **when** the output is accepted,
   **then** no more than 20 unique conceptual tags remain.
4. **Given** model output containing more than five novel tags, **when** the output is accepted,
   **then** no more than the first five valid, importance-ranked novel tags remain.
5. **Given** model output that manufactures combinations such as multiple
   `Nuclear-{Attack,Defense,Offense}-{Planning,Policy,Doctrine}` variants without substantive
   support, **when** tag inference is performed, **then** the model is instructed not to generate
   those combinations and the hard limits prevent an excessive result even if it does.
6. **Given** the same normalized conceptual tag appears more than once, **when** results are
   finalized, **then** it appears exactly once.
7. **Given** `NATO`, `Brussels`, or a person's name is already represented as an entity, **when** the
   same value is proposed as a conceptual tag, **then** the conceptual duplicate is removed even if
   it originated in seed or reused vocabulary.

---

### User Story 2 - Evolve Vocabulary Without Feedback Amplification (Priority: P2)

As an archive researcher, I want useful model-discovered tags to become reusable vocabulary after
independent recurrence, while one-off inventions remain available in their source documents without
immediately influencing every subsequent document.

**Why this priority**: Vocabulary evolution is a central capability, but immediate promotion turns a
single hallucination into a self-reinforcing archive-wide convention.

**Independent Test**: Process documents containing the same non-seed conceptual tag. Verify that the
tag is retained locally after its first appearance, is not yet presented as preferred vocabulary,
and becomes established and reusable after appearing in a second independent document.

**Acceptance Scenarios**:

1. **Given** a valid novel tag appears in one document, **when** the next document is processed,
   **then** that tag remains stored in the first document but is not presented as preferred
   vocabulary.
2. **Given** the same normalized novel tag appears in two independent documents, **when** later
   documents are processed, **then** it is treated as established vocabulary and may be offered to
   the model for reuse.
3. **Given** a seed tag has not yet appeared in any document, **when** tag inference runs, **then**
   the seed tag remains available to the model.
4. **Given** a one-off speculative tag, **when** many later documents are processed, **then** the tag
   is not amplified solely because it exists in one earlier document.
5. **Given** existing archive output already contains a tag in at least two independent documents,
   **when** the archive is scanned before a run, **then** that tag qualifies as established without
   requiring a separate migration.

---

### User Story 3 - Control Reasoning for Tag Inference (Priority: P3)

As a command-line user, I want the existing model-reasoning option to govern tag inference as well
as document metadata extraction, so that I can tune instruction-following behavior consistently for
the entire metadata run.

**Why this priority**: Different models vary in their ability to distinguish substantive concepts
from plausible expansions, and the user needs direct control over the reasoning level used for tag
selection.

**Independent Test**: Run metadata processing with each accepted reasoning value and inspect mocked
tag-inference requests to verify that every tag request receives the selected, correctly typed value
without changing the number of inference calls.

**Acceptance Scenarios**:

1. **Given** metadata processing uses `--model-think=False`, **when** tag inference runs, **then**
   every tag-inference request has reasoning explicitly disabled.
2. **Given** metadata processing uses `--model-think=low`, `medium`, or `high`, **when** tag inference
   runs, **then** every tag-inference request receives the selected effort level.
3. **Given** the option is omitted, **when** tag inference runs, **then** it receives the established
   default value of `medium`.
4. **Given** a document uses multiple inference windows, **when** tags are extracted, **then** every
   window uses the same command-scoped reasoning value.

### Edge Cases

- A document supports fewer than five conceptual tags; the system returns only the supported tags
  and does not fill a quota.
- All proposed tags are novel; at most five valid novel tags are retained.
- The model returns duplicate tags with differences in case, punctuation, leading hash marks, or
  spacing; they count as one normalized tag.
- A proposed conceptual tag matches any meaningful component of a hierarchical entity path, such as
  either the surname or given identity of a person; the conceptual tag is removed.
- A seed or established tag conflicts with an entity in the current document; entity separation
  takes precedence over vocabulary protection.
- Several windows propose overlapping tags; document-level deduplication and limits are applied to
  the aggregate result, not independently as the final decision for each window.
- The model returns more tags than allowed but puts the most relevant tags first; retained tags
  follow that declared importance order after invalid and duplicate entries are removed.
- A tag appears repeatedly within one document; this still counts as one document for promotion.
- A previously established tag later becomes rare; it remains established because automatic
  demotion would make archive behavior unstable.
- A non-substantive administrative stub legitimately receives no conceptual tags.
- The model proposes an acronym that names an organization rather than a concept; it is kept only as
  an entity.
- Existing archive documents are not rewritten merely because promotion status or inference rules
  change.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST treat `USEFUL_TAGS.yaml` as a seed vocabulary and MUST NOT restrict
  conceptual output exclusively to entries from that file.
- **FR-002**: The tag-inference instructions MUST ask for a small, importance-ranked set of principal
  archival concepts, with a target range of 5–12 tags for substantive documents and no requirement
  to fill that range when fewer concepts are supported.
- **FR-003**: The instructions MUST require each conceptual tag to represent a substantively
  discussed concept and MUST reject tags based only on implication, a passing mention, or lexical
  association.
- **FR-004**: The instructions MUST prohibit speculative combinations, Cartesian-product tag
  families, synonyms, grammatical variants, and broader or narrower variants unless each retained
  concept is independently and substantively supported.
- **FR-005**: The instructions MUST require the model to prefer an available seed or established tag
  when it expresses the same concept, while still permitting a genuinely distinct novel tag.
- **FR-006**: The instructions MUST require conceptual tags to exclude people, organizations,
  states, cities, and other values already represented as entities.
- **FR-007**: The instructions MUST tell the model to return conceptual tags in descending order of
  importance so that deterministic truncation retains the model's strongest selections.
- **FR-008**: The system MUST normalize and remove exact conceptual duplicates before applying tag
  limits, using case-insensitive and punctuation-normalized comparison while preserving one
  canonical output form.
- **FR-009**: The system MUST enforce a hard document-level maximum of 20 unique conceptual tags.
- **FR-010**: The system MUST enforce a hard document-level maximum of five novel conceptual tags.
- **FR-011**: When a result exceeds a hard limit, the system MUST retain valid tags according to the
  model's declared importance order after normalization, entity separation, and deduplication.
- **FR-012**: Hard limits MUST apply to both single-pass and multi-window inference, with the final
  aggregate treated as one document result.
- **FR-013**: The system MUST deterministically remove a conceptual tag that duplicates a normalized
  entity name or meaningful entity-path component in the same document.
- **FR-014**: Seed or reused status MUST NOT exempt a conceptual tag from entity-collision removal.
- **FR-015**: A valid novel tag within the five-tag novelty budget MUST be retained in its source
  document immediately.
- **FR-016**: A non-seed tag MUST become established after appearing in at least two independent
  documents, where repeated appearances within one document count only once.
- **FR-017**: Seed and established tags MUST be made available as preferred vocabulary during later
  tag inference.
- **FR-018**: A novel tag seen in only one document MUST NOT be presented as preferred vocabulary to
  later documents, although it MUST remain stored in its source document.
- **FR-019**: Existing archive outputs MUST contribute to establishment counts during the normal
  pre-run scan, without requiring a separate migration or vocabulary database.
- **FR-020**: Once a tag becomes established, it MUST remain established for the duration of the
  archive run; automatic rarity-based demotion is outside this feature.
- **FR-021**: The existing case-insensitive `--model-think` values `False`, `low`, `medium`, and
  `high` MUST also govern every tag-inference request started by the metadata command.
- **FR-022**: The reasoning default for tag inference MUST be `medium`, consistent with the metadata
  command default, and `False` MUST be transmitted as a disabled boolean rather than text.
- **FR-023**: A multi-window document MUST apply the same selected reasoning setting to every
  tag-inference window.
- **FR-024**: The feature MUST NOT add model calls beyond the existing tag-inference calls.
- **FR-025**: Final archive output MUST continue to contain a simple conceptual-tag list; the feature
  MUST NOT request, store, or expose structured provenance, source phrases, justifications, novelty
  flags, or alternative-tag deliberation for novel tags.
- **FR-026**: Existing archive documents MUST NOT be rewritten automatically; users adopt revised
  tag selection by rerunning metadata processing when desired.
- **FR-027**: The system MUST permit an empty conceptual-tag list for non-substantive administrative
  stubs and MUST NOT manufacture tags to meet the target range.
- **FR-028**: Meaningful acronyms MUST obey the same substantive-concept, entity-separation, novelty,
  deduplication, and hard-limit rules as all other conceptual tags.

### Key Entities

- **Seed Tag**: A curated starting concept supplied by `USEFUL_TAGS.yaml`; always eligible for prompt
  reuse but still subject to document relevance and entity separation.
- **Novel Tag**: A valid model-created conceptual tag not present in the seed vocabulary and not yet
  observed in two independent documents; retained locally within the novelty budget but not yet
  preferred in later prompts.
- **Established Tag**: A seed tag or a model-created tag observed in at least two independent
  documents; available as preferred vocabulary in subsequent inference.
- **Document Tag Set**: The normalized, entity-separated, deduplicated, importance-ordered set of
  conceptual tags for one document, limited to 20 total and five novel tags.
- **Reasoning Setting**: The command-scoped selection `False`, `low`, `medium`, or `high` applied to
  document metadata extraction and every tag-inference request in the same metadata run.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In 100% of validation cases, a document contains no more than 20 unique conceptual
  tags and no more than five novel conceptual tags.
- **SC-002**: In 100% of validation cases, normalized duplicate conceptual tags appear only once in
  final document output.
- **SC-003**: In 100% of validation cases, a conceptual tag that duplicates an entity name or
  meaningful entity-path component is absent from the final conceptual-tag set.
- **SC-004**: On the supplied over-generation pattern, at least 75% of unsupported combinatorial or
  redundant conceptual tags are eliminated while every independently reviewer-supported concept
  within the hard limits remains available.
- **SC-005**: A valid novel tag is retained on first occurrence and becomes preferred vocabulary
  after occurrence in exactly two independent documents in 100% of lifecycle tests.
- **SC-006**: A one-document novel tag is never promoted solely because it was generated repeatedly
  within that document.
- **SC-007**: All four accepted reasoning selections, including the disabled boolean, reach every
  tag-inference request with the correct value in 100% of command and multi-window tests.
- **SC-008**: Tag control and vocabulary evolution add zero additional model inference calls per
  document.
- **SC-009**: Reviewers can distinguish the principal concepts in a generated tag section without
  encountering repeated tags or mechanically generated tag families in at least 95% of a curated
  validation sample.

## Assumptions

- The order of tags returned by the model represents descending importance because the prompt will
  explicitly require that ordering.
- A hard maximum of 20 total conceptual tags and five novel conceptual tags per document provides a
  conservative safety boundary while preserving useful vocabulary growth.
- Two independent document occurrences are sufficient to promote a model-created tag from novel to
  established vocabulary.
- Existing per-document tag scans provide enough information to determine independent document
  occurrence counts; no new persistent registry is required.
- Semantic judgments such as substantive relevance, synonymy, and whether a combined phrase is a
  genuine concept remain primarily the responsibility of the language model instructions.
- Deterministic enforcement is limited to normalization, exact deduplication, entity collisions,
  document-count promotion, typed reasoning propagation, and numeric limits.
- Existing topic classification behavior and the Person entity hierarchy remain unchanged.
- Structured provenance for novel tags is explicitly outside scope.
