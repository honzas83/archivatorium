# Feature Specification: Item Type Metadata

**Feature Branch**: `032-item-type-metadata`

**Created**: 2026-06-15

**Status**: Draft

**Input**: User description: "We will add a metadata field (at the beginning of of the metdata structure) describing the type of the item. We should use: correspondence, report, study, meeting_minutes, working_paper, schedule, corrigendum, agenda, press_release, note, directive, other as possible values for this field. Add specific LLM instructions, if needed."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Classify Each Item by Document Type (Priority: P1)

As an archive curator reviewing generated metadata, I need every processed item to include a clear document-type value near the start of its metadata so that I can sort, filter, and audit mixed archival collections by item form.

**Why this priority**: The new field has no value unless every generated metadata record exposes it consistently and before the rest of the metadata details.

**Independent Test**: Process representative correspondence, reports, agendas, meeting minutes, directives, and unclear items, then verify each generated metadata record begins with an item-type field containing one allowed value.

**Acceptance Scenarios**:

1. **Given** a source document that is clearly a letter, cable, or other exchanged communication, **When** metadata is generated, **Then** the metadata includes `correspondence` as the item type.
2. **Given** a source document that is clearly a report, **When** metadata is generated, **Then** the metadata includes `report` as the item type.
3. **Given** any successfully processed source document, **When** the generated metadata is reviewed, **Then** the item-type field appears before all existing metadata fields.

---

### User Story 2 - Use a Closed Type Vocabulary (Priority: P2)

As a metadata maintainer, I need item-type values to come only from the approved list so that downstream review, spreadsheets, and filtering do not fragment into near-duplicate labels.

**Why this priority**: Free-text type labels would quickly create vocabulary drift and reduce the usefulness of the new field.

**Independent Test**: Review generated outputs for varied document forms and verify every item-type value is exactly one of the approved values with no pluralization, title casing, spaces, or ad hoc synonyms.

**Acceptance Scenarios**:

1. **Given** a document that could be described informally as "minutes", **When** metadata is generated, **Then** the item type is `meeting_minutes`, not `minutes`, `Meeting Minutes`, or another variant.
2. **Given** a document that is clearly a press notice, **When** metadata is generated, **Then** the item type is `press_release`, not `press notice` or `release`.
3. **Given** a document type that does not match any approved category clearly, **When** metadata is generated, **Then** the item type is `other`.

---

### User Story 3 - Provide Consistent Classification Guidance (Priority: P3)

As an operator relying on automated metadata generation, I need the item-type classification instructions to distinguish similar document forms consistently so that ambiguous archival wording does not produce unstable results.

**Why this priority**: Several allowed values are adjacent in meaning, such as note, working paper, report, and study; clear guidance reduces inconsistent classification.

**Independent Test**: Run metadata generation against samples with similar forms and verify the selected item type follows documented guidance for each allowed value.

**Acceptance Scenarios**:

1. **Given** a source primarily explaining, advising, summarizing, or reporting status/findings, **When** metadata is generated, **Then** the item type is `report`.
2. **Given** a source containing an ordered list of topics for an upcoming meeting, **When** metadata is generated, **Then** the item type is `agenda`.
3. **Given** a source correcting a previous document, **When** metadata is generated, **Then** the item type is `corrigendum`.

### Edge Cases

- A document contains multiple sections, appendices, or enclosures with different forms; the item type should describe the primary item, not every included section.
- A document title uses archival abbreviations or non-English labels; classification should use document structure and contents, not only the title.
- A document primarily explains, advises, summarizes, or reports status/findings; `report` should be selected.
- A document is a brief internal annotation without substantive report or directive structure; `note` should be preferred over `report`.
- A document presents research or analysis but is explicitly labeled as a working draft; `working_paper` should be preferred over `study` or `report`.
- A document is a correction, erratum, or amendment notice whose main purpose is to correct another item; `corrigendum` should be selected even if the text is short.
- If the source is too damaged, fragmentary, or generic to classify reliably, the item type should be `other`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every generated metadata record MUST include an item-type field.
- **FR-002**: The item-type field MUST appear before all previously existing metadata fields wherever the structured metadata is presented.
- **FR-003**: The item-type value MUST be exactly one of: `correspondence`, `report`, `study`, `meeting_minutes`, `working_paper`, `schedule`, `corrigendum`, `agenda`, `press_release`, `note`, `directive`, `other`.
- **FR-004**: Metadata generation MUST NOT emit item-type values outside the approved vocabulary, including synonyms, translated labels, pluralized labels, title-cased labels, or labels with spaces.
- **FR-005**: The item-type field MUST be present for all successfully generated metadata even when the source document type is uncertain.
- **FR-006**: When no approved type is clearly supported by the source, the item-type value MUST be `other`.
- **FR-007**: Classification guidance MUST describe how to distinguish each approved item type from adjacent or commonly confused types.
- **FR-008**: Classification guidance MUST appear before the title, summary, and other field instructions in the metadata extraction prompt so non-reasoning structured-output models see the first emitted field first.
- **FR-009**: The metadata schema field order, extraction prompt rule order, and generated metadata presentation order MUST follow the same hierarchy for fields generated by the LLM: item type, title, summary, abstract, authorship, date/code, language/location, correspondence details, and references.
- **FR-010**: Classification guidance MUST instruct automated metadata generation to use filename, document title, headings, opening formula, structure, stated purpose, and content together when selecting the item type.
- **FR-011**: Classification guidance MUST instruct automated metadata generation to prefer the primary document form over secondary attachments, quoted material, appendices, or incidental references.
- **FR-012**: Classification guidance MUST instruct automated metadata generation to select `correspondence` for letters, cables, telegrams, messages, or other exchanged communications when that is the primary document form.
- **FR-013**: Classification guidance MUST instruct automated metadata generation to classify documents by primary function.
- **FR-014**: Classification guidance MUST instruct automated metadata generation to select `report` for documents primarily reporting findings, status, events, activities, outcomes, advice, explanations, or summaries.
- **FR-015**: Classification guidance MUST instruct automated metadata generation to select `study` for analytical or research-oriented documents whose primary purpose is examination or evaluation of a topic.
- **FR-016**: Classification guidance MUST instruct automated metadata generation to select `meeting_minutes` for records of meeting proceedings, attendance, discussion, or actions taken.
- **FR-017**: Classification guidance MUST instruct automated metadata generation to select `working_paper` for draft, discussion, preparatory, or working documents intended to support deliberation.
- **FR-018**: Classification guidance MUST instruct automated metadata generation to select `schedule` for timetables, calendars, program schedules, or ordered time plans.
- **FR-019**: Classification guidance MUST instruct automated metadata generation to select `corrigendum` for corrections, errata, or notices whose main purpose is to amend a previous document.
- **FR-020**: Classification guidance MUST instruct automated metadata generation to select `agenda` for lists of meeting topics, items for discussion, or planned order of business.
- **FR-021**: Classification guidance MUST instruct automated metadata generation to select `press_release` for public-facing press statements, communiques, or media releases.
- **FR-022**: Classification guidance MUST instruct automated metadata generation to select `note` for brief notes, annotations, informal records, or short observations that are not substantive reports or directives.
- **FR-023**: Classification guidance MUST instruct automated metadata generation to select `directive` for documents whose primary purpose is to issue instructions, orders, requirements, or policy direction.
- **FR-024**: Existing metadata fields MUST retain their current meaning and relative order after the new item-type field.
- **FR-025**: Review and export surfaces that present structured metadata MUST include the item-type field consistently with generated document metadata.
- **FR-026**: Existing metadata records without an item-type value MUST remain readable; any newly generated or regenerated metadata MUST include the item-type field.

### Key Entities *(include if feature involves data)*

- **Metadata Record**: The structured descriptive information generated for an archival item, now beginning with an item-type field followed by existing metadata fields.
- **Item Type**: The controlled document-form classification assigned to a metadata record from the approved vocabulary.
- **Approved Item-Type Vocabulary**: The closed list of allowable item-type values: correspondence, report, study, meeting_minutes, working_paper, schedule, corrigendum, agenda, press_release, note, directive, and other.
- **Source Document**: The archival item being processed, whose title, headings, structure, stated purpose, and content provide evidence for item-type selection.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a representative validation set, 100% of successfully generated metadata records include the item-type field before all previously existing metadata fields.
- **SC-002**: In generated metadata, 100% of item-type values are exact members of the approved vocabulary.
- **SC-003**: In a validation set containing at least one clear example for each approved non-`other` type, at least 90% of clear examples receive the expected item type on first generation.
- **SC-004**: In a validation set of unclear, fragmentary, or unsupported document forms, 100% of accepted uncertain classifications use `other` rather than an unapproved label.
- **SC-005**: Existing metadata review and export workflows show the item type for newly generated records without removing, renaming, or reordering existing fields other than placing the new field first.

## Assumptions

- The field name will be chosen to clearly communicate document form; `item_type` is the expected name unless an existing naming convention requires a different equivalent.
- The approved vocabulary is intentionally closed for this feature; adding or renaming values is out of scope.
- `other` is the fallback for genuinely unclear or unsupported document forms, not a replacement for careful classification when a listed value is clearly supported.
- The item type describes the primary source document, not attachments, quoted documents, filing wrappers, or incidental references.
- Newly generated and regenerated metadata must include the field; historical outputs may be updated only when they are regenerated through normal processing.
