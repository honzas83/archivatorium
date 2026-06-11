# Feature Specification: Fix Tag and Interlink Bugs

**Feature Branch**: `029-fix-tag-interlinks`

**Created**: 2026-06-11

**Status**: Draft

**Input**: User description: "In this specification, we will fix bugs. First, parsing of generated tags should replace slashes with dashes to avoid malformed generated tag warnings for organization and state tags. Next, in interlink, do not use full paths for linked sibling language variants, but use bare target filenames instead."

## Clarifications

### Session 2026-06-11

- Q: Should topic assignment limits and counter hints change? → A: Allow unlimited assigned topics; use top 100 topic counter items in context.
- Q: Should filename-only targets apply beyond language versions? → A: Apply filename-only targets globally to all document-to-document Markdown links, including references and body links.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Keep Generated Entity Tags Valid (Priority: P1)

As a vault generator user, I want generated organization and state tags containing slash-like names to be normalized into valid tag names, so that useful entity metadata is retained instead of being ignored with warnings.

**Why this priority**: Malformed generated tags are currently discarded, which causes metadata loss and noisy processing output.

**Independent Test**: Can be fully tested by processing documents whose generated entity tags include names such as `OTAN/NATO`, `NAC/DP`, `Council/DPC`, and `USA/California`, then confirming that the output includes valid normalized tags and no malformed-tag warnings for those cases.

**Acceptance Scenarios**:

1. **Given** a generated organization tag whose entity name contains one or more slashes, **When** metadata is parsed, **Then** each slash inside the entity name is represented as a dash and the tag is accepted.
2. **Given** a generated state tag whose entity name contains one or more slashes, **When** metadata is parsed, **Then** each slash inside the entity name is represented as a dash and the tag is accepted.
3. **Given** generated entity tags that already conform to the expected organization or state tag shape, **When** metadata is parsed, **Then** those tags remain valid and are not unnecessarily changed.

---

### User Story 2 - Use Portable Interlinks Between Documents (Priority: P2)

As a reader of exported vault notes, I want generated links between documents to use only the target filename, so that references, body links, and language-version links remain readable and portable if the vault folder is moved or viewed from the current note location.

**Why this priority**: Full-path links are harder to read and can become fragile when linked document files are already addressable by filename.

**Independent Test**: Can be fully tested by generating interlinks for documents with nested target paths and confirming that language-version, references, and body links point to filenames such as `NPG-D(74)12_FRE.md` or `NPG(STUDY)38_ENG.md` rather than paths containing parent folders.

**Acceptance Scenarios**:

1. **Given** a note with a linked sibling language variant in the same document set, **When** interlinks are generated, **Then** the displayed link target uses only the sibling note filename.
2. **Given** a note with a generated references-row link to another document, **When** interlinks are generated, **Then** the reference link target uses only the target note filename.
3. **Given** a note with a generated body link to another document, **When** interlinks are generated, **Then** the body link target uses only the target note filename.
4. **Given** a target note whose filename contains parentheses, hyphens, or underscores, **When** interlinks are generated, **Then** the filename is preserved exactly in the link target.
5. **Given** existing non-generated links outside document interlinking, **When** interlinks are generated, **Then** those unrelated links are not rewritten solely by this feature.

---

### User Story 3 - Preserve All Justified Topic Assignments (Priority: P3)

As a vault generator user, I want metadata extraction to assign every clearly justified taxonomy topic and use a broader set of resume-derived topic hints, so that substantive documents are not under-tagged by an artificial topic cap.

**Why this priority**: Topic coverage affects vault navigation and downstream indexes; hard caps can omit relevant topics from long or dense documents.

**Independent Test**: Can be fully tested by processing a document whose content clearly justifies more than the previous topic limit and confirming all justified topics are retained, while the prompt context includes the top 100 topic counter items when that many exist.

**Acceptance Scenarios**:

1. **Given** a substantive document that clearly supports more than the previous maximum number of taxonomy topics, **When** generated tags are extracted, **Then** all clearly justified topics are retained without a hard maximum.
2. **Given** resume-derived topic counters with at least 100 entries, **When** tagging context is prepared, **Then** the top 100 topic counter items are available to the model as context.
3. **Given** resume-derived topic counters with fewer than 100 entries, **When** tagging context is prepared, **Then** every available topic counter item is included.

---

### Edge Cases

- Generated organization or state entity names may contain multiple slashes; every slash within the entity name should become a dash.
- Generated entity names may contain surrounding whitespace around slash-separated parts; normalized tags should not introduce empty or malformed path segments.
- Generated tags that are malformed for reasons other than slash-containing entity names should still be rejected or reported according to existing validation behavior.
- Interlink targets may be generated inside nested document folders; all generated document-to-document links should still use the target filename only.
- Filename-only links must not change the visible link label, such as `French` or `NPG(STUDY)/38`.
- Long or dense substantive documents may justify more than 10 taxonomy topics; justified topics should not be dropped solely because of a fixed count limit.
- Resume-derived topic counters may contain more than 100 entries; only the top 100 are required in tagging context to keep context bounded.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST accept generated organization entity tags whose entity name contains slashes by replacing each slash in the entity name with a dash before validation.
- **FR-002**: The system MUST accept generated state entity tags whose entity name contains slashes by replacing each slash in the entity name with a dash before validation.
- **FR-003**: The system MUST preserve the existing entity tag category prefix while normalizing only the generated entity name portion.
- **FR-004**: The system MUST prevent malformed generated-tag warnings for organization and state tags when the only invalid condition is a slash inside the entity name.
- **FR-005**: The system MUST continue to ignore or warn about generated tags that remain malformed after normalization.
- **FR-006**: The system MUST generate all document-to-document interlinks using the target note filename only.
- **FR-007**: The system MUST preserve the visible label of generated interlinks while changing only the destination target format.
- **FR-008**: The system MUST avoid introducing parent-folder paths into generated document-to-document interlink destinations.
- **FR-009**: The system MUST preserve valid filenames exactly when creating filename-only link destinations, including punctuation and spacing that are part of the filename.
- **FR-010**: The system MUST leave unrelated link types outside generated document interlinking unchanged.
- **FR-011**: The system MUST NOT impose a hard maximum on the number of assigned taxonomy topics when each topic is clearly justified by the document content.
- **FR-012**: The system MUST make the top 100 resume-derived topic counter items available as tagging context when at least 100 topic counter items exist.
- **FR-013**: The system MUST make all available resume-derived topic counter items available as tagging context when fewer than 100 topic counter items exist.
- **FR-014**: The system MUST keep resume-derived topic counter items subordinate to the approved taxonomy; counter context must not authorize non-taxonomy topics.

### Key Entities

- **Generated Entity Tag**: A tag proposed by metadata extraction for an organization or state, consisting of a category prefix and an entity name.
- **Normalized Entity Name**: The accepted entity name after slash characters in a generated organization or state name are replaced with dashes.
- **Generated Document Interlink**: A generated Markdown link from one vault document note to another vault document note, including references, body links, and language-version links.
- **Language Variant Interlink**: A generated document interlink from one note to a sibling note representing another language version of the same or closely related document.
- **Sibling Note Filename**: The target note's filename, including extension, without parent folder components.
- **Assigned Topic**: A taxonomy topic selected for a document because the source text clearly justifies it.
- **Topic Counter Context**: Resume-derived topic counter items supplied to tagging as contextual hints, bounded to the top 100 items.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of generated organization and state tags matching the reported slash-containing examples are accepted after normalization.
- **SC-002**: Processing documents with slash-containing organization or state names produces zero malformed-tag warnings for those names when no other malformed condition exists.
- **SC-003**: 100% of generated document-to-document interlinks in generated notes use filename-only targets.
- **SC-004**: Existing visible interlink labels remain unchanged in generated notes after the destination format change.
- **SC-005**: A representative vault export containing both affected tag examples and affected interlink examples completes with no loss of accepted metadata compared with the normalized expected output.
- **SC-006**: A document fixture with more than 10 clearly justified taxonomy topics retains all justified topics in generated metadata.
- **SC-007**: A tagging context built from 120 resume-derived topic counter items includes exactly the top 100 topic items.

## Assumptions

- This bug fix applies to generated organization and state entity tags, matching the reported warning examples.
- Replacing slashes with dashes is the desired canonical representation for slash-containing generated organization and state names.
- Filename-only interlinks are intended for generated document-to-document links where the target filename is sufficient from the current note context.
- Existing validation should remain responsible for rejecting generated tags that are malformed for other reasons.
- Topic counter context remains a hint source only; the approved taxonomy remains authoritative for topic assignment.
