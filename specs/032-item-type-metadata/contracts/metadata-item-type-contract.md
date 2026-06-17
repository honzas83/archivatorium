# Contract: Metadata Item Type

## Generated Metadata Contract

Every newly generated or regenerated document metadata record must include `item_type` as the first structured metadata field.

```yaml
---
item_type: correspondence
title: Example Title
summary: Example one-sentence summary.
...
---
```

## Allowed Values

`item_type` must be exactly one of:

```text
correspondence
report
study
meeting_minutes
working_paper
schedule
corrigendum
agenda
press_release
note
directive
other
```

No synonyms, translated labels, plural labels, title-cased labels, or labels with spaces are valid.
Sources are classified by primary function, usually `report` for explanatory, advisory, status, findings, or summary documents.

## Extraction Contract

Metadata extraction must classify the primary document form using the source filename, title, headings, opening formula, structure, stated purpose, and content.

The extraction prompt must present `item_type` selection before title, summary, abstract, and other field instructions so the first prompt rule matches the first structured metadata field.

When classification is uncertain or unsupported, the extraction result must use:

```yaml
item_type: other
```

The classifier must not create values outside the allowed vocabulary.

## Presentation Contract

The structured metadata callout must present item type before the previous metadata fields.

```markdown
> [!info] Metadata
> | Key | Value |
> | --- | --- |
> | Item Type | correspondence |
> | Title | Example Title |
```

Existing fields keep their current meaning and relative order after the new field.

## XLSX Export Contract

The generated `metadata_index.xlsx` workbook must include an `Item Type` core metadata column populated from `item_type`.

Expected row behavior:

| Metadata `item_type` | XLSX `Item Type` |
|----------------------|------------------|
| `report`             | `report`         |
| `meeting_minutes`    | `meeting_minutes` |
| missing historical value | blank unless regenerated metadata supplies `other` |
