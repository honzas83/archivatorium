# Data Model: NATO Topic Taxonomy V2

## TaxonomyDocument

Represents a loaded hierarchy before it is flattened for classification.

| Field | Type | Rules |
|---|---|---|
| `schema_version` | integer, optional for legacy | Must equal `2` for v2; absent means legacy schema |
| `classification_policy` | ClassificationPolicy, required for v2 | All policy fields must be non-empty |
| `categories` | list of CategoryDefinition | Non-empty; v2 has exactly the six specified categories |

## ClassificationPolicy

| Field | Type | Meaning |
|---|---|---|
| `substantive_subject_rule` | non-empty string | Defines analysis/decision/proposal/operation/sustained-description threshold |
| `omission_rule` | non-empty string | Prefers omission and explicitly permits no thematic topics |
| `insufficient_evidence_rule` | non-empty string | Rejects mentions, entities, titles, citations, meetings, and administrative form alone |

For a legacy taxonomy, `TaggingService` supplies the same built-in effective policy without mutating
the source file.

## CategoryDefinition

| Field | Type | Rules |
|---|---|---|
| `category` | non-empty string | Cannot contain `/`; normalized component cannot be empty |
| `description` | non-empty string | Included in every flattened member topic |
| `topics` | list of TopicDefinition | Non-empty |

## TopicDefinition

| Field | Type | Rules |
|---|---|---|
| `topic` | non-empty string | Cannot contain `/`; normalized component cannot be empty |
| `description` | non-empty string | Defines substantive inclusion and nearest exclusions |
| `positive_samples` | multiline string | Must yield at least one non-empty example line |
| `negative_samples` | multiline string | Must yield at least one non-empty example line |

The canonical `topic_id` is derived as
`normalize_tag_component(category.category)/normalize_tag_component(topic.topic)`. It must be unique.

## FlattenedTopic

Internal classifier-ready representation. It remains compatible with the existing topic-description
key and adds category context.

| Field | Type | Rules |
|---|---|---|
| `id` | string | Unique canonical `Category/Topic` path and only selectable identifier |
| `category` | string | Canonical category component |
| `category_description` | string | Complete source category description |
| `description` | string | Complete source topic description |
| `positive_samples` | list of string | All non-empty source examples in order |
| `negative_samples` | list of string | All non-empty source examples in order |

## TopicAssignment

Existing externally published topic result.

| Field | Type | Rules |
|---|---|---|
| `topic` | string | Normalized path must occur in the approved flattened-ID set |
| `reason` | string | Existing explanatory text contract remains unchanged |

An empty collection of topic assignments is valid. No quotation matching or evidence-repair state is
introduced by this feature.

## ValidationCase

Local evaluation record for a reviewed source document.

| Field | Type | Meaning |
|---|---|---|
| `source` | local path or identifier | Located under gitignored `data/039-nato-taxonomy-v2/` |
| `expected_topics` | set of v2 paths | Substantively supported topics |
| `excluded_topics` | set of v2 paths | Known weak/incidental matches that must be omitted |
| `notes` | string | Human rationale used for review, not sent as classifier context |

## State Transitions

### Taxonomy preparation

`raw file -> parsed mapping -> normalized structure -> validated taxonomy -> flattened prompt context`

Any invalid transition raises a taxonomy validation error; it never becomes an empty approved set.

### Topic assignment

`model candidate -> normalized path -> approved path | rejected path -> deduplicated output`

Only approved paths enter cross-window aggregation or metadata output. The earliest assignment wins
when the same normalized path occurs more than once. Empty output is a successful state.
