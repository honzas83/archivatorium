# Data Model: Hierarchical Person Entities and Model Reasoning Control

## Person Entity

Represents one named individual emitted by tag extraction and retained through archive metadata.

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `surname` | string | Yes | Non-empty after tag normalization; must identify a surname without guessing; excludes titles and roles. |
| `given_identity` | string or absent | No | Full given name(s), initials, or both; one path component after normalization. |
| `relative_path` | string | Derived | `Person/<surname>` or `Person/<surname>/<given_identity>`. |
| `archive_path` | string | Derived | `Entities/<relative_path>`. |

### Validation rules

- A surname is mandatory; a given identity is optional.
- The relative path has exactly two components for surname-only identity or three components when a
  given identity is present.
- Initials are uppercased and separated by single hyphens: `K-W` and `K. W.` become `K-W`, and
  Joseph M.A.H. becomes `Joseph-M-A-H`.
- Full hyphenated names remain full names and keep meaningful tag-safe hyphenation.
- Compound surnames and multiple given names each remain within their own single component.
- Honorifics, ranks, offices, and role modifiers such as minister and secretary are excluded.
- A missing/ambiguous surname, empty component, or surplus component makes a generated candidate
  invalid and it is omitted with an actionable warning.

### Examples

| Source identity | Canonical relative path | Outcome |
|-----------------|-------------------------|---------|
| K-W Andrae | `Person/Andrae/K-W` | Full identity with normalized initials |
| K. W. Andrae | `Person/Andrae/K-W` | Same canonical identity |
| Joseph M.A.H. Luns | `Person/Luns/Joseph-M-A-H` | Full given name plus normalized initials |
| Joseph Luns | `Person/Luns/Joseph` | Full identity |
| Andrae, given name unknown | `Person/Andrae` | Valid surname-only identity |
| Minister Andrae | `Person/Andrae` | Role excluded |
| Secretary General Joseph Luns | `Person/Luns/Joseph` | Office excluded |
| Unresolved damaged surname | — | Candidate omitted |

### Relationships

- A tagging result contains zero or more Person entities.
- A canonical tag collection stores each Person identity as a lowercased relative value for counts
  and its normalized case-preserving archive path for output and indexing.
- Multiple documents can reference the same Person path.
- Multiple Person paths can share a surname while remaining distinct through `given_identity`.

### Lifecycle

```text
source mention
  → model candidate Person path
  → semantic surname/given split
  → structural validation and component normalization
  → initials hyphenation when applicable
  → document aggregation/deduplication
  → Entities/ prefix and Markdown output
  → canonical parsing, counters, export, and surname index
```

Existing Markdown follows only the parsing-and-indexing portion; it is never rewritten by this
lifecycle.

## Model Reasoning Setting

Represents the reasoning choice for one OCR or metadata command run.

| Field | Type | Required | Rules |
|-------|------|----------|-------|
| `cli_value` | choice | No | Case-insensitive `False`, `low`, `medium`, or `high`; defaults to `medium`. |
| `request_value` | boolean or effort string | Derived | `False` becomes boolean false; other values remain `low`, `medium`, or `high`. |
| `command` | OCR or metadata | Yes | Determines the governed call sites. |

### Propagation rules

- OCR: the request value governs Qwen 3.8 OCR requests. Other OCR profiles retain their established
  reasoning behavior.
- Metadata: the request value governs primary structured extraction and conditional final-date
  extraction.
- Tagging: remains explicitly non-thinking and does not consume this setting.
- Invalid choices have no state transition: command validation fails before file discovery or model
  interaction.

### State transitions

```text
CLI text
  → validate accepted choice
  → convert to False | low | medium | high
  → store in command-scoped processor/engine configuration
  → attach to each governed model request
```
