# Research: Hierarchical Person Entities and Model Reasoning Control

## Decision: Use a surname-first path with one optional identity component

**Decision**: Newly generated people use `Person/<surname>/<given-name-or-initials>` when given-name
information is known and `Person/<surname>` otherwise. No additional hierarchy components are valid.

**Rationale**: This directly provides surname browsing while preserving the user's explicit
surname-only case. Limiting the depth prevents titles, offices, and roles from becoming identity
modifiers.

**Alternatives considered**:

- Require both surname and given name: rejected because the user explicitly requires surname-only
  entities when the given name is unknown.
- Add role/title levels: rejected because minister, secretary, rank, and similar modifiers are not
  part of the person's identity.

## Decision: Combine semantic prompting with deterministic structural normalization

**Decision**: Make the tagging prompt responsible for identifying surname and given-name semantics,
then run generated Person candidates through shared deterministic normalization before aggregation
and again when parsing Markdown.

**Rationale**: Code can reliably enforce component count, empty values, tag-safe spelling, initials,
and prohibited modifier tokens, but cannot reliably infer global naming conventions without context.
Prompt-only enforcement would allow malformed paths to reach downstream consumers.

**Alternatives considered**:

- Prompt-only formatting: rejected because it cannot guarantee path depth or initials normalization.
- Derive surnames mechanically from the final token of a combined name: rejected because compound
  surnames, name particles, and surname-first source forms make that unsafe.

## Decision: Normalize initials as hyphen-separated letters within the given identity

**Decision**: Normalize every initials sequence inside the optional identity component to uppercase
letters separated by single hyphens. Thus `K-W` and `K. W.` both become `K-W`, while Joseph M.A.H.
becomes `Joseph-M-A-H`. Preserve full given-name tokens under normal tag-safe normalization.

**Rationale**: A single visible separator preserves the individual initials and produces the user's
required forms without damaging meaningful hyphens in full names such as Jean-Paul.

**Alternatives considered**:

- Concatenate initials as `KW` or `MAH`: rejected because the user requires `K-W` and
  `Joseph-M-A-H`.
- Preserve source punctuation exactly: rejected because K-W, K. W., and similar forms should resolve
  to one canonical identity.

## Decision: Accept both Person depths in the canonical parser

**Decision**: The Markdown parser accepts the surname-only and surname-plus-given forms, stores the
relative identity as `surname[/given]`, and retains the full normalized raw path.

**Rationale**: Preflight counters, reuse hints, entity sections, indexes, and XLSX export all depend
on the canonical parser. The raw-path set already supports variable depth; only Person validation and
value construction currently assume one combined component.

**Alternatives considered**:

- Flatten the path after parsing: rejected because it would discard the hierarchy and merge names.
- Rewrite existing Markdown during parsing: rejected because parsing must remain non-mutating and
  migration is outside scope.

## Decision: Specialize People-index grouping by surname

**Decision**: Sort Person paths by their suffix after `Entities/Person/` and derive the index letter
and visible person label from the surname-first identity rather than the final path component.

**Rationale**: The generic index currently uses the final component as its label and alphabetic key,
which would group `Person/Andrae/K-W` under K. A People-specific selector preserves the new browsing
semantics while leaving state, organization, and conceptual indexes unchanged.

**Alternatives considered**:

- Keep generic final-component grouping: rejected because it defeats surname-first navigation.
- Change all alphabetical indexes: rejected because only Person paths changed meaning.

## Decision: Use one converted reasoning type at command boundaries

**Decision**: Both commands accept case-insensitive `False`, `low`, `medium`, and `high`; a shared
conversion maps false to boolean `False` and keeps effort levels as strings. The default is `medium`.

**Rationale**: Ollama distinguishes disabled reasoning from named effort levels. Converting once at
the CLI boundary avoids passing the string `"False"`, and a shared definition keeps OCR and metadata
behavior aligned.

**Alternatives considered**:

- Pass all choices as strings: rejected because `"False"` is not the disabled boolean contract.
- Add separate boolean and effort options: rejected because it creates contradictory combinations
  and differs from the requested interface.

## Decision: Scope OCR control to the Qwen 3.8 reasoning call

**Decision**: Change the Qwen 3.8 profile default from high to medium and apply the OCR option as an
override at that request. Preserve the existing absence or disabled state for standard, GLM, and
FireRed profiles.

**Rationale**: The user identified the Qwen 3.8 fixed `think` field as the OCR call site. Applying a
medium default to every profile would silently change unrelated models and violate the feature's
compatibility boundary.

**Alternatives considered**:

- Apply the option to every OCR profile: rejected because standard and FireRed currently omit the
  field and GLM explicitly disables it.
- Create separate per-profile flags: rejected as unnecessary scope expansion.

## Decision: Scope metadata control to both document extraction calls

**Decision**: Pass the selected setting to primary structured metadata extraction and the
conditional final-date extraction. Keep tag extraction explicitly non-thinking.

**Rationale**: These are the two metadata call sites identified by the requested diff. Applying the
setting to tagging would alter a deliberately non-thinking second pass and broaden the request.

**Alternatives considered**:

- Apply the setting to every model call under the metadata command: rejected because the user named
  the exact `medium` call sites and tagging has an established explicit `False` behavior.
- Configure only primary extraction: rejected because fallback date extraction must behave
  consistently within the same command run.

## Decision: Adopt the new Person format by rerunning metadata

**Decision**: Do not add a migration command or rewrite existing archive files. New or rerun metadata
uses the new hierarchy.

**Rationale**: The workflow already regenerates metadata, and mechanical conversion cannot reliably
separate old combined names into surname and given-name components.

**Alternatives considered**:

- Split old paths on hyphens: rejected because hyphens can belong to either name component.
- Rewrite paths while indexing: rejected because indexing must not mutate source documents.
