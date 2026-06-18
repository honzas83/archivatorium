# Research: Item Type Metadata

## Decision: Add `item_type` as a first-class metadata extraction field

**Rationale**: The project already uses a Pydantic metadata schema as the structured contract for LLM extraction. Adding `item_type` there makes the field available during metadata generation, validation, frontmatter rendering, metadata callouts, and export without creating a second classification path.

**Alternatives considered**:

- Post-process document text after extraction: rejected because it would duplicate LLM classification logic and require a separate classifier.
- Encode item type as a tag: rejected because the requirement is a metadata field at the beginning of the metadata structure, not another discovery tag.
- Add a separate command: rejected because item type should be part of normal metadata generation.

## Decision: Use a closed string vocabulary with a safe default

**Rationale**: The feature depends on exact values for review and filtering. A closed vocabulary prevents drift such as "minutes", "meeting minutes", and "Meeting Minutes". The default/fallback value should be `other` so old records remain readable and uncertain documents can still be represented without inventing labels.

**Alternatives considered**:

- Free-text item type: rejected because it would fragment the field.
- Required non-default value with validation failure on uncertainty: rejected because damaged or fragmentary archival sources must still process.
- Optional field: rejected for newly generated records because the specification requires every generated metadata record to include it.

## Decision: Put classification instructions in the metadata prompt and schema description

**Rationale**: Item type is extracted from title, headings, opening formula, structure, stated purpose, and content. The existing metadata prompt is the right user-facing extraction context. Schema descriptions keep the structured response contract aligned with the prompt.

**Alternatives considered**:

- Prompt-only change: rejected because output validation and field presence should be part of the structured metadata model.
- Schema-only change: rejected because adjacent categories need explicit classification guidance to reduce inconsistent LLM choices.

## Decision: Preserve existing metadata order after placing `item_type` first

**Rationale**: The specification requires the new field at the beginning while preserving existing fields' meaning and relative order. The existing `processor_metadata._prepare_obsidian_metadata` primary key list controls generated frontmatter and metadata callout order, so adding `item_type` as the first key satisfies the requirement with minimal surface area.

**Alternatives considered**:

- Let Pydantic field order alone control output: rejected because the processor already normalizes, filters, and reorders metadata before rendering.
- Add item type only to frontmatter: rejected because metadata callouts and export surfaces also present structured metadata.

## Decision: Include item type in the XLSX metadata index

**Rationale**: The spec calls out review and export surfaces. The XLSX metadata index is the main structured export, so it should include an "Item Type" column near the front of the core metadata columns.

**Alternatives considered**:

- Leave export unchanged: rejected because users would be unable to filter generated indexes by item type.
- Generate a separate type index page: rejected as extra scope not required by the feature.
