# Data Model: Item Type Metadata

## Metadata Record

Represents structured descriptive metadata generated for an archival source document.

### Fields Added

- `item_type`: controlled document-form classification for the source item.

### Existing Field Relationship

- `item_type` appears before all existing metadata fields in generated frontmatter and metadata callouts.
- Existing metadata fields retain their current meanings and relative order after `item_type`.
- LLM-generated metadata fields share one hierarchy across schema, extraction prompt, and rendered output: `item_type`, `title`, `summary`, `abstract`, authorship, date/code, language/location, correspondence details, and `references`. Processor-generated fields such as pages, citekey, and source are inserted only during rendering.
- Existing records without `item_type` remain readable and may be regenerated to receive the field.

### Validation Rules

- Newly generated metadata records must include `item_type`.
- Empty or missing generated `item_type` values resolve to `other`.
- Accepted values are exactly:
  - `correspondence`
  - `report`
  - `study`
  - `meeting_minutes`
  - `working_paper`
  - `schedule`
  - `corrigendum`
  - `agenda`
  - `press_release`
  - `note`
  - `directive`
  - `other`

## Item Type

Represents one selected document-form value for a source item.

### Selection Rules

- Select one value only.
- Classify the primary document form rather than attachments, quoted material, appendices, filing wrappers, or incidental references.
- Use filename, title, headings, opening formula, structure, stated purpose, and content together.
- Use `other` when the document is too damaged, fragmentary, generic, or unsupported to classify reliably.
- In metadata extraction prompts, place item-type selection before title, summary, and other field instructions because `item_type` is the first emitted structured field.

### Type Guidance

- `correspondence`: letters, cables, telegrams, messages, or other exchanged communications.
- `report`: documents primarily reporting findings, status, events, activities, outcomes, advice, explanations, or summaries.
- `study`: analytical or research-oriented documents whose main purpose is examination or evaluation.
- `meeting_minutes`: records of meeting proceedings, attendance, discussion, or actions taken.
- `working_paper`: draft, discussion, preparatory, or working documents supporting deliberation.
- `schedule`: timetables, calendars, program schedules, or ordered time plans.
- `corrigendum`: corrections, errata, or amendment notices whose main purpose is to correct another item.
- `agenda`: lists of meeting topics, discussion items, or planned order of business.
- `press_release`: public-facing press statements, communiques, or media releases.
- `note`: brief notes, annotations, informal records, or short observations that are not substantive reports or directives.
- `directive`: documents whose primary purpose is issuing instructions, orders, requirements, or policy direction.
- `other`: unclear, unsupported, damaged, fragmentary, or otherwise unmatched document forms.

## Metadata Index Entry

Represents one generated document row in the structured metadata index.

### Fields Added

- `Item Type`: exported display column populated from metadata `item_type`.

### Validation Rules

- `Item Type` appears in the core metadata columns near the beginning of the index.
- Missing historical values are exported as blank or `other` only if normal metadata regeneration supplied `other`; export must not invent a new unapproved value.
