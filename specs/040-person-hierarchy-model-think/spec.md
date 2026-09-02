# Feature Specification: Hierarchical Person Entities and Model Reasoning Control

**Feature Branch**: `040-person-hierarchy-model-think`

**Created**: 2026-09-02

**Status**: Draft

**Input**: User description: "Represent Person named entities as Person/surname/given-name, allow
surname-only paths when the given name is unknown, compact initials such as K-W to KW, exclude role
modifiers, and add --model-think=False|low|medium|high to the OCR and metadata commands."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate Canonical Person Paths (Priority: P1)

As an archive researcher, I want every recognized person to use a surname-first hierarchical path so
that people are grouped and browsed consistently by family name.

**Why this priority**: Person paths are durable archive metadata. Inconsistent ordering fragments a
person's record and makes the people index harder to navigate.

**Independent Test**: Process documents containing full names, initials, and surname-only mentions,
then verify that every Person entity starts with the surname and adds a normalized given-name or
initials component only when known, including `Entities/Person/Andrae/KW` for K-W Andrae.

**Acceptance Scenarios**:

1. **Given** a document unambiguously names K-W Andrae, **When** metadata is generated, **Then** the
   resulting entity path is `Entities/Person/Andrae/KW`.
2. **Given** a document unambiguously names Joseph Luns, **When** metadata is generated, **Then** the
   resulting entity path is `Entities/Person/Luns/Joseph` rather than a single combined name.
3. **Given** several documents use equivalent forms of one person's complete name, **When** their
   metadata is generated, **Then** the normalized paths resolve to the same surname-first identity.
4. **Given** only the surname Andrae is known, **When** metadata is generated, **Then** the resulting
   entity path is `Entities/Person/Andrae`.
5. **Given** a person's surname cannot be identified without guessing, **When** metadata is
   generated, **Then** no malformed or guessed Person path is emitted.
6. **Given** a person is described as a minister or secretary, **When** metadata is generated,
   **Then** that role is not included in the Person path.

---

### User Story 2 - Select Model Reasoning Effort (Priority: P2)

As a command-line user, I want to select the model reasoning effort for OCR and metadata processing
so that I can balance speed, resource use, and output quality for each run.

**Why this priority**: Different archive workloads require different inference tradeoffs, and a fixed
reasoning level prevents users from controlling those tradeoffs.

**Independent Test**: Run each command once for every accepted `--model-think` value and verify that
all relevant model requests use the selected value without changing other command behavior.

**Acceptance Scenarios**:

1. **Given** an OCR run using the reasoning-capable OCR mode, **When** the user supplies
   `--model-think=low`, **Then** the OCR model request uses low reasoning effort.
2. **Given** a metadata run, **When** the user supplies `--model-think=high`, **Then** both the main
   metadata extraction and any follow-up date extraction use high reasoning effort.
3. **Given** either command, **When** the user supplies `--model-think=False`, **Then** reasoning is
   explicitly disabled for the relevant model requests.
4. **Given** either command without `--model-think`, **When** processing begins, **Then** medium
   reasoning effort is used for the model calls governed by this option.

---

### User Story 3 - Preserve Navigable Person Metadata (Priority: P3)

As an archive researcher, I want generated entity sections, counts, parsing, and people indexes to
retain the new hierarchy so that surname-first Person paths remain usable throughout the archive.

**Why this priority**: Correct generation alone is insufficient if later archive stages reject,
flatten, or mis-index the path.

**Independent Test**: Feed a generated surname-first Person path through the archive's normal
metadata and indexing workflow and verify that it remains intact and appears under the correct person.

**Acceptance Scenarios**:

1. **Given** generated metadata contains `Entities/Person/Andrae/KW`, **When** the metadata is
   parsed, counted, exported, and indexed, **Then** the same complete hierarchy is retained.
2. **Given** two different people share a surname, **When** the people index is generated, **Then**
   their distinct given-name paths remain separately identifiable beneath that surname.
3. **Given** an existing archive created with the old Person path form, **When** this feature is
   installed but metadata is not rerun, **Then** existing files are not silently rewritten.

### Edge Cases

- Given names or surnames containing spaces, hyphens, initials, apostrophes, diacritics, or name
  particles must remain recognizable after normal tag-safe normalization.
- Multiple initials must be uppercase and concatenated without spaces, periods, or hyphens; for
  example, K-W and K. W. both become `KW`.
- A person with multiple given names must retain the complete given-name portion as one hierarchical
  component rather than creating extra hierarchy levels.
- A compound surname must remain one surname component when the document makes that structure clear.
- Honorifics, ranks, offices, titles, and role modifiers such as minister or secretary are not parts
  of either the surname or given-name component.
- An invalid `--model-think` value must be rejected before document processing begins with a message
  that lists the accepted values.
- Reasoning output must not leak into saved OCR text or generated metadata when reasoning is enabled.
- OCR modes or model interactions outside the calls governed by this option must retain their
  established behavior.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST represent every newly generated Person entity as
  `Person/<surname>/<given-name-or-initials>` when the given name is known, or `Person/<surname>` when
  it is not, before the archive-wide `Entities/` prefix is applied.
- **FR-002**: The system MUST generate `Entities/Person/Andrae/KW` for an unambiguous reference to
  K-W Andrae.
- **FR-003**: The system MUST keep a known given name or initials separate from the surname and MUST
  NOT emit the former combined-name form for newly generated Person entities.
- **FR-004**: The system MUST exclude honorifics, ranks, offices, titles, and other role modifiers,
  including minister and secretary, from Person paths.
- **FR-005**: When a surname is known but a given name or initials are not, the system MUST emit the
  surname-only Person path rather than omit the person or invent another component.
- **FR-006**: The system MUST omit a Person entity when the surname itself cannot be identified
  without guessing.
- **FR-007**: The system MUST normalize multiple initials as uppercase contiguous letters without
  punctuation, spaces, or hyphens, so K-W and K. W. both produce `KW`.
- **FR-008**: The system MUST preserve complete compound surnames and multiple given names within
  their respective single hierarchy components after normal tag-safe normalization.
- **FR-009**: All downstream handling of Person entities, including validation, aggregation,
  document entity sections, exports, and people indexes, MUST accept and preserve the complete
  surname-first hierarchy.
- **FR-010**: Distinct people who share a surname MUST remain distinguishable by their given-name or
  initials component whenever that information is available.
- **FR-011**: The OCR and metadata commands MUST each expose a `--model-think` option.
- **FR-012**: The option MUST accept exactly the logical values `False`, `low`, `medium`, and `high`,
  with `False` meaning that model reasoning is explicitly disabled.
- **FR-013**: Accepted option values MUST be case-insensitive so that `False` and `false` have the
  same meaning.
- **FR-014**: When the option is omitted, its value MUST default to `medium`.
- **FR-015**: For the reasoning-capable OCR request identified in this feature, the selected value
  MUST replace the fixed reasoning effort.
- **FR-016**: For metadata processing, the selected value MUST govern both the primary structured
  extraction and the follow-up date extraction request when that follow-up occurs.
- **FR-017**: An unsupported option value MUST stop the command before any document is processed and
  explain the accepted values.
- **FR-018**: Adding the option MUST NOT alter model selection, prompts, output locations, overwrite
  behavior, or unrelated OCR-mode behavior.
- **FR-019**: Existing archive files MUST NOT be automatically migrated or rewritten; users adopt
  the new Person hierarchy by rerunning metadata processing.
- **FR-020**: Saved OCR and metadata output MUST continue to exclude private model reasoning content.

### Key Entities

- **Person Entity**: A named individual represented by a mandatory surname and, when known, an
  optional given name or compacted initials. Titles and roles are excluded from the identity.
- **Person Path**: The archive tag path `Entities/Person/<surname>[/<given-name-or-initials>]` used
  consistently in generated metadata and downstream navigation.
- **Model Reasoning Setting**: A per-command-run choice of disabled, low, medium, or high reasoning
  effort, defaulting to medium and applied to the model interactions in scope.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In a reviewed sample of at least 100 person mentions, 100% of newly generated Person
  paths begin with the reviewer-approved surname and include no titles or role modifiers.
- **SC-002**: In the same sample, at least 95% of people resolve to the reviewer-approved surname and
  optional given-name split; 100% of known initials are compacted without separators, and 100% of
  surname-only cases remain valid surname-only paths.
- **SC-003**: All generated hierarchical Person paths survive parsing, aggregation, document output,
  export, and people-index generation without losing or reordering any present name component.
- **SC-004**: For both OCR and metadata commands, 100% of accepted reasoning choices are reflected in
  every governed model interaction, including conditional follow-up interactions.
- **SC-005**: Invalid reasoning choices are rejected before the first document is processed in 100%
  of validation tests.
- **SC-006**: Existing command invocations that omit the new option complete with medium reasoning
  effort and otherwise unchanged observable behavior.
- **SC-007**: No private reasoning content appears in any saved OCR or metadata output across all
  enabled reasoning levels.

## Assumptions

- `medium` is the intended default because it is the fixed value identified for both requested
  processing workflows.
- The textual value `False` means an explicit disabled boolean rather than a reasoning level named
  "false"; matching is case-insensitive for command-line usability.
- A valid Person entity requires an identifiable surname. A given name or compacted initials are
  added only when known; surname-only mentions remain valid, while unresolved surnames are omitted.
- Normal archive tag normalization continues to make spaces and punctuation tag-safe while
  preserving meaningful name hyphens, apostrophes, diacritics, and name particles as far as the
  existing output format permits; separators between initials are removed as required above.
- Existing metadata is regenerated by rerunning the metadata command; migration of previously
  generated Person paths is outside this feature.
- Only the OCR model call corresponding to the user-identified fixed reasoning setting is governed
  by the new OCR option. Other OCR profiles retain their existing reasoning behavior.
