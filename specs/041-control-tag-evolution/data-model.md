# Data Model: Controlled Tag Evolution

No persistent schema is added. The feature refines in-memory roles around the existing conceptual
tag strings and per-document counters.

## ConceptualTagCandidate

An ordered candidate returned by the existing tagging model call.

| Field | Type | Rules |
|---|---|---|
| `display_value` | `str` | Canonical Obsidian-safe value retained for output |
| `comparison_key` | `str` | Normalized and case-folded exact identity |
| `importance_position` | `int` | Original model order, or aggregate frequency/rank order for windows |
| `is_known` | `bool` | Key exists in the document's seed-plus-established snapshot |
| `is_novel` | `bool` | Logical inverse of `is_known`; not persisted or exposed |

Validation transitions:

- Raw model string → normalized candidate.
- Candidate is discarded if empty, low-value, an exact duplicate, or collides with an entity/topic
  under the finalization rules.
- A novel candidate is discarded when five earlier valid novel candidates have been retained.
- Any candidate is discarded when 20 earlier valid candidates have been retained.

## VocabularySnapshot

Immutable inference context for one document.

| Field | Type | Source |
|---|---|---|
| `seed_keys` | `set[str]` | Normalized `USEFUL_TAGS.yaml` entries |
| `established_keys` | `set[str]` | Reuse-hint tags promoted at document count ≥2 |
| `preferred_display_values` | `list[str]` | Deterministically ranked prompt vocabulary |

The snapshot is created before tag inference and shared by every window. Tags produced by the
current document cannot alter its novelty classification.

## TaggingReuseHints

Existing frozen transfer object between `MetadataProcessor` and `TaggingService`.

| Field | Type | Revised meaning |
|---|---|---|
| `preferred_conceptual_tags` | `list[str]` | Non-seed conceptual tags established in at least two documents |
| `preferred_entities` | `dict[str, list[str]]` | Existing category-specific entity vocabulary; unchanged |
| `preferred_topics` | `list[str]` | Existing taxonomy-subordinate topic hints; unchanged |

## ConceptualDocumentCounts

Existing `Counter[str]` on `MetadataProcessor`, paired with a new run-scoped established set.

- Key: canonical parsed conceptual tag relative to `#Tags/`, normalized consistently with existing
  counters.
- Value: number of independently parsed output documents containing the tag.
- Repetition inside one document contributes once because `CanonicalTags` stores tag paths as a
  set before counter ingestion.
- Value `1`: local/novel, retained in its document but excluded from later preferred hints.
- Value `>=2`: added to the monotonic established set and eligible for later preferred hints.
- Established entries are not removed from that set during a run.

## DocumentTagSet

Final `AggregatedTaggingResult.conceptual_tags: list[str]`.

Invariants:

- Importance order is stable after invalid candidates are removed.
- Comparison keys are unique.
- Total length is at most 20.
- At most five members are novel relative to the document snapshot.
- No member duplicates a normalized entity name or meaningful entity-path component.
- Output contains no novelty or provenance metadata.

## ReasoningSetting

Existing shared `ModelThink` type:

```text
False | "low" | "medium" | "high"
```

The metadata command creates one typed value and supplies it to primary metadata extraction,
conditional date extraction, and every tag-inference window. Default: `"medium"`.
