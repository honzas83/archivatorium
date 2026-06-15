# Data Model: Prompt Tag Normalization

## LLM Response Category Order

The tagging prompt and structured response schema present categories in this order so
the model resolves broad classification before entities and leaves residual discovery
tags for last:

1. `topic_tags`: Categories/Topics from the approved taxonomy.
2. `entity_tags`: States, organisations, cities, and persons.
3. `conceptual_tags`: Substantive archival Tags that are not duplicate entities or topic components.

## Entity Tag

Represents a real-world entity mentioned in source text.

**Fields**:

- `type`: One of `State`, `Org`, `City`, or `Person`.
- `canonical_name`: Preferred display/tag value for the entity.
- `hierarchical_path`: Tag path emitted by the metadata generator, such as `Org/NATO` or `City/Belgium/Brussels`.
- `source_mention`: Source-text mention that justifies the entity.

**Validation rules**:

- State tags use `State/<name>`.
- Organisation tags use `Org/<name>`.
- City tags use `City/<country>/<city>`.
- Person tags use `Person/<name>`.
- Names use English canonical forms when a clear equivalent exists.
- Names use title case except standard acronyms, which remain all caps.
- Ambiguous OCR-damaged strings must not be converted into invented entities.

## Topic Tag

Represents a taxonomy-backed subject classification.

**Fields**:

- `topic_path`: Flat taxonomy value in `Category/Topic` form.
- `reason`: Textual explanation that includes a direct source citation.

**Validation rules**:

- Topic path must come from the approved taxonomy.
- Topic reason must include direct quoted evidence from the source text.
- This feature must not reduce the existing topic evidence requirement.
- Topic extraction is a mandatory multi-label classification step for substantive archival text; all supported approved taxonomy topics should be emitted, and an empty `topic_tags` list is valid only when no approved taxonomy topic is clearly supported.

## Conceptual Tag

Represents a substantive archival concept, acronym, or reusable discovery term.

**Fields**:

- `canonical_tag`: Preferred conceptual tag path or term.
- `source_mention`: Source-text support for the concept.
- `reuse_signal`: Whether the term appears in useful tags or resumed vocabulary hints.

**Validation rules**:

- Substantive documents require at least 1 conceptual tag while still allowing every clearly justified useful conceptual tag.
- Meaningful all-caps acronyms remain eligible when justified.
- Non-acronym all-caps words are normalized to title case.
- Conceptual tags must not duplicate entity names or topic components exactly.
- After entity tags are chosen, conceptual tags must strictly exclude the same entity's exact name, aliases, acronyms, translations, expanded-name variants, punctuation/case variants, hyphenation variants, and compacted normalized forms.
- A conceptual tag related to an entity is valid only when it adds substantive archival meaning beyond the entity itself.
- Conceptual tags must not include both an abbreviation and expanded full-name form for the same concept when a canonical choice is clear.
- For well-known NATO-domain terms, the standard acronym is preferred over the expanded full-name form.

## Canonical Form

Represents the preferred normalized representation for a generated value.

**Fields**:

- `language`: English for states, cities, and organisations when clear.
- `casing`: Title case except standard acronyms.
- `spelling`: Corrected spelling when OCR damage is obvious from context.
- `hierarchy`: Required tag path structure for the category.

**Relationships**:

- One canonical form can replace multiple source variants.
- Canonical forms apply to entity tags first and conceptual tags where casing/acronym behavior is relevant.
- Canonical conceptual forms collapse clear abbreviation/full-name pairs for the same concept.

## Sample Finding

Represents a vocabulary-quality issue observed in the v6 analysis.

**Fields**:

- `pattern`: Case mismatch, multilingual duplicate, OCR corruption, or hierarchy confusion.
- `examples`: Concrete observed variants from the sample.
- `impact`: Fragmentation count or qualitative search/review impact.
- `expected_prompt_guidance`: Rule or example that addresses the pattern.

**Validation rules**:

- Each high-impact sample pattern from the spec must be represented in prompt guidance.
- Findings drive prompt wording only; they do not create new runtime data structures.

## State Transitions

No persisted entity state changes are introduced. The only lifecycle is generation-time normalization:

1. Source text contains a mention or damaged mention.
2. Prompt instructs the model to determine whether the intended value is clear.
3. Clear values emit canonical tags.
4. Ambiguous damaged values are omitted or left unconverted rather than invented.
