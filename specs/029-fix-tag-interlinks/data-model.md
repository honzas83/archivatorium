# Data Model: Fix Tag and Interlink Bugs

## Generated Entity Tag

Represents a tag produced by metadata extraction and discovered in Markdown content.

**Fields**:

- `raw_text`: Original tag text, including leading `#`.
- `prefix`: Top-level tag family, expected to be `Entities` for this feature.
- `entity_type`: Entity category, relevant values are `Org` and `State`.
- `entity_name`: Name component after the entity type.

**Validation rules**:

- Organization and state tags must resolve to exactly one entity name component after normalization.
- Empty normalized components are invalid.
- Unsupported entity types remain invalid.
- Tags malformed for reasons other than slash-containing organization/state names keep existing rejection behavior.

## Normalized Entity Name

Represents the accepted canonical entity name stored after parser normalization.

**Fields**:

- `display_value`: Case-preserving normalized name used in raw tag paths.
- `lookup_value`: Lowercase normalized value used in entity sets.

**Validation rules**:

- Any slash inside a generated organization or state name becomes a dash.
- Multiple slashes become multiple dash separators without introducing empty path components.
- Existing component normalization, such as whitespace-to-dash behavior, continues to apply.

## Language Variant Interlink

Represents one generated document interlink type: a metadata-row link from one document to another language version of the same archive code.

**Fields**:

- `label`: Human-readable language name, such as `French`.
- `stored_target_path`: Existing path value recorded in the interlink map.
- `link_target`: Markdown destination emitted in the language-versions row.

**Validation rules**:

- The `label` is unchanged.
- The `link_target` for sibling language variants is the basename of `stored_target_path`.
- Parent folder components must not appear in the language-version link target.
- Filename punctuation, including parentheses, hyphens, and underscores, is preserved.

## Generated Document Interlink

Represents any generated Markdown link from one vault document note to another vault document note.

**Fields**:

- `label`: Visible link text, such as an archive code or language name.
- `stored_target_path`: Existing vault-relative path used internally for lookup and self-link detection.
- `link_target`: Filename-only Markdown destination emitted in generated content.

**Validation rules**:

- Applies to references rows, body links, and language-version links.
- The `label` is unchanged.
- The emitted `link_target` is the basename of `stored_target_path`.
- Parent folder components must not appear in the emitted link target.

## Sibling Note Filename

Represents the target note filename used in a language-version interlink.

**Fields**:

- `filename`: Final path component including `.md` extension.

**Validation rules**:

- Must not include parent directories.
- Must preserve the original filename exactly.

## Assigned Topic

Represents a taxonomy topic selected for a document because the source text clearly supports it.

**Fields**:

- `topic`: Hierarchical taxonomy path in `Category/Topic` form.
- `reason`: Short justification tied to the source text.

**Validation rules**:

- Must be selected from the approved taxonomy.
- Must be clearly justified by the document content.
- Must not be removed solely because a fixed count limit has been reached.
- Multiple assigned topics are deduplicated by normalized topic path while retaining the best available reason.

## Topic Counter Context

Represents resume-derived topic counter hints supplied to the tagging prompt.

**Fields**:

- `counter_items`: Topic counter entries ordered by descending frequency.
- `prompt_items`: Items exposed to the model as contextual hints.

**Validation rules**:

- If at least 100 counter items exist, `prompt_items` contains exactly the top 100 items.
- If fewer than 100 counter items exist, `prompt_items` contains every available item.
- Topic counter context is subordinate to the approved taxonomy and must not authorize non-taxonomy topic assignments.

## Relationships

- A `Generated Entity Tag` produces one `Normalized Entity Name` when accepted.
- A `Generated Document Interlink` derives its `link_target` from the target note filename.
- A `Language Variant Interlink` is a specialized `Generated Document Interlink` whose label is the target language.
- Existing document and code maps remain the source for identifying generated document interlinks.
- A document can have any number of `Assigned Topic` values when each is justified by the text and present in the taxonomy.
- `Topic Counter Context` influences topic consistency only as prompt context; the approved taxonomy remains authoritative.
