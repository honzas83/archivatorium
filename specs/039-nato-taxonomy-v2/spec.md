# Feature Specification: NATO Topic Taxonomy V2

**Feature Branch**: `039-nato-taxonomy-v2`

**Created**: 2026-09-02

**Status**: Draft

**Input**: User description: "Implement all suggested NATO topic hierarchy changes in a new NATO_themes_v2.yaml, correct taxonomy flattening and tagging behavior, and apply a universal substantive-subject rule."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Classify Documents by Substantive Subject (Priority: P1)

As an archive researcher, I want thematic topics to describe what a document is substantively about rather than every concept, organization, or country it happens to mention, so that topic browsing returns relevant documents.

**Why this priority**: Validation found systematic false-positive topic assignments, especially for extended deterrence and nuclear sharing. Correct subject classification is the primary user value of the taxonomy.

**Independent Test**: Apply the new taxonomy to a validation set containing substantive policy documents, routine meeting notices, agendas, transmittal notes, corrigenda, and documents with incidental nuclear or organizational references. Confirm that only substantively supported topics are assigned and that an empty topic list is accepted when appropriate.

**Acceptance Scenarios**:

1. **Given** a document that merely mentions nuclear weapons, several NATO countries, or a multinational meeting, **When** topics are assigned, **Then** extended deterrence or nuclear sharing is not assigned unless the document substantively discusses the defining relationship.
2. **Given** a routine meeting notice, agenda, distribution list, cover note, or corrigendum with no substantive thematic content, **When** topics are assigned, **Then** the document may receive no thematic topics.
3. **Given** a document that substantively analyzes a taxonomy topic, **When** topics are assigned, **Then** the topic is included with evidence demonstrating the defining relationship rather than merely repeating a keyword.
4. **Given** several potentially relevant topics, **When** the evidence for one topic is weak or incidental, **Then** that topic is omitted even if other well-supported topics are assigned.

---

### User Story 2 - Distinguish Overlapping Nuclear and Alliance Topics (Priority: P1)

As an archive researcher, I want overloaded topics separated into historically and analytically distinct concepts, so that I can distinguish deterrent guarantees, weapons deployment, nuclear release, strike planning, consultation, command organization, and infrastructure.

**Why this priority**: The current combined labels blur distinct concepts and accounted for the largest cluster of validation disagreements.

**Independent Test**: Classify representative documents for nuclear guarantees, forward deployment, dual-key release, target selection, political consultation, command appointments, and infrastructure funding. Each document should receive the narrow topic matching its substantive content without automatically receiving adjacent topics.

**Acceptance Scenarios**:

1. **Given** a document about the credibility of a nuclear guarantee to non-nuclear allies, **When** it is classified, **Then** it can receive Extended Nuclear Deterrence without automatically receiving Nuclear Sharing and Forward Deployment.
2. **Given** a document about allied custody, basing, delivery roles, or forward deployment of nuclear weapons, **When** it is classified, **Then** it can receive Nuclear Sharing and Forward Deployment without automatically receiving Extended Nuclear Deterrence.
3. **Given** a document about dual-key arrangements, authentication, approval, delegation, or release authority, **When** it is classified, **Then** it can receive Nuclear Release Authority without automatically receiving Nuclear Strategy and Strike Planning.
4. **Given** a document that only mentions SACEUR, SACLANT, SHAPE, or a visit to a headquarters, **When** it is classified, **Then** it does not receive a command-structure or infrastructure topic on that basis alone.
5. **Given** a document about command appointments or reporting relationships, **When** it is classified, **Then** it can receive Command Structure and Appointments; given a document about pipelines, radar sites, physical facilities, or common infrastructure funding, it can instead receive NATO Infrastructure and Common Funding.

---

### User Story 3 - Use Complete Taxonomy Context (Priority: P2)

As a taxonomy maintainer, I want all classification-relevant category and topic guidance to reach the classifier, so that hierarchy descriptions, positive examples, and negative examples influence decisions consistently.

**Why this priority**: Category descriptions currently provide useful distinctions for maintainers but are not available during classification, weakening the intended hierarchy.

**Independent Test**: Inspect the classification-ready representation of the new taxonomy and confirm that each topic retains its full category path, category description, topic description, positive examples, and negative examples without silently discarding classification-relevant content.

**Acceptance Scenarios**:

1. **Given** a category with a description and several topics, **When** the taxonomy is prepared for classification, **Then** every topic retains the category name and category description together with its own guidance.
2. **Given** a topic with multiple positive and negative examples, **When** the taxonomy is prepared, **Then** all non-empty examples remain associated with the correct topic.
3. **Given** malformed or incomplete taxonomy entries, **When** the taxonomy is loaded, **Then** maintainers receive a clear failure rather than silently receiving an incomplete approved taxonomy.

---

### User Story 4 - Verify Topic Evidence (Priority: P2)

As an archive researcher, I want every topic justification grounded in the document text, so that fabricated quotations and keyword-only explanations do not appear as evidence.

**Why this priority**: Validation identified unsupported and occasionally fabricated supporting quotations. A better hierarchy cannot correct evidence that is not present in the source.

**Independent Test**: Submit topic assignments containing exact quotations, quotations differing only in conservative whitespace, and quotations absent from the document. Accept the grounded cases and reject or recover the unsupported case without publishing it as valid evidence.

**Acceptance Scenarios**:

1. **Given** a topic justification containing a quotation found in the source, **When** the result is validated, **Then** the topic assignment is retained.
2. **Given** a quotation that differs from the source only by line wrapping or repeated whitespace, **When** it is validated, **Then** conservative normalization may establish the match without changing words.
3. **Given** a quotation that cannot be found in the source, **When** the result is validated, **Then** the unsupported assignment is not published as valid and the system attempts the configured recovery behavior.
4. **Given** a real quotation that merely contains a topic keyword, **When** the topic relationship is evaluated, **Then** the topic is omitted unless the quotation demonstrates the topic's defining subject.

---

### User Story 5 - Adopt V2 Without Damaging Existing Archives (Priority: P3)

As an archive maintainer, I want the revised taxonomy introduced as a separate version with an explicit path mapping, so that existing archives remain reproducible and renamed or split topics can be migrated deliberately.

**Why this priority**: Renaming and splitting topic paths can otherwise fragment indexes or silently change the meaning of existing archive tags.

**Independent Test**: Confirm that the original taxonomy remains available unchanged, the v2 taxonomy can be selected independently, and every renamed, moved, or split v1 topic has documented migration guidance.

**Acceptance Scenarios**:

1. **Given** an existing workflow that selects the original taxonomy, **When** the v2 taxonomy is added, **Then** the original taxonomy and its outputs remain available.
2. **Given** a new workflow selecting the v2 taxonomy, **When** a document is classified, **Then** it uses only approved v2 paths.
3. **Given** a v1 topic that was renamed, moved, or split, **When** a maintainer reviews migration guidance, **Then** the old path and all applicable new paths are explicit, including cases requiring reclassification rather than automatic one-to-one replacement.

### Edge Cases

- A substantive document has no approved thematic topic even though it requires ordinary conceptual tags.
- A document consists only of an agenda, meeting schedule, cover sheet, distribution list, transmittal letter, cancellation, corrigendum, or empty scan.
- A cover note and one or more substantive attachments are present in the same file and concern different subjects.
- A topic is named only in the title of a cited or attached document, not discussed in the document under classification.
- A country or organization is present only in an attendance list, distribution list, address block, or reference list.
- OCR corruption changes a topic-bearing phrase, acronym, quotation, country name, or organization name.
- A quotation spans a line or page break, contains repeated whitespace, or uses typographic punctuation that differs from the extracted text.
- A classification-ready taxonomy contains a missing category name, missing topic name, duplicate topic path, empty description, or examples of an unexpected type.
- A document supports multiple topics, including two closely related topics, with independent substantive evidence for each.
- Historical status depends on document date, such as Finland or Sweden being discussed as neutral or non-aligned during the Cold War.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The product MUST provide a separately selectable NATO topic taxonomy version named `NATO_themes_v2.yaml` while preserving the existing NATO taxonomy unchanged.
- **FR-002**: The v2 taxonomy MUST organize topics under these top-level categories: Nuclear Doctrine and Deterrence; Nuclear Planning, Deployment, and Control; Alliance Governance and Institutions; Treaties and Arms Control; Military Operations and Capabilities; and Geopolitics and Crises.
- **FR-003**: The v2 taxonomy MUST retain all existing approved topics unless this specification explicitly renames, splits, moves, or corrects them.
- **FR-004**: The combined Extended Deterrence and Tactical Nuclear Sharing topic MUST be replaced by two distinct topics: Extended Nuclear Deterrence and Nuclear Sharing and Forward Deployment.
- **FR-005**: Extended Nuclear Deterrence MUST require substantive discussion of a nuclear-armed ally's protective guarantee, including its credibility, reassurance, cohesion, or deterrent effect; multinational participation, generic NATO nuclear policy, or weapons stationed in Europe MUST NOT be sufficient alone.
- **FR-006**: Nuclear Sharing and Forward Deployment MUST require substantive discussion of allied basing, custody, delivery, planning, deployment, or employment roles; mere mention of nuclear weapons in Europe or nuclear-site security MUST NOT be sufficient alone.
- **FR-007**: Command and Control Authority MUST be replaced by Nuclear Release Authority, narrowly covering approval, authentication, delegation, dual-key arrangements, safeguards, or release of nuclear weapons.
- **FR-008**: Nuclear Strategy and Strike Planning MUST require substantive discussion of war plans, target selection, yields, strike timing, force employment, or execution planning; meeting schedules, generic nuclear-force references, and administrative discussion MUST be explicit negative examples.
- **FR-009**: Specific Commands and Infrastructure MUST be replaced by Command Structure and Appointments plus NATO Infrastructure and Common Funding.
- **FR-010**: Command Structure and Appointments MUST require substantive discussion of appointments, command responsibilities, command boundaries, reporting relationships, or organizational structure; mention of a command, headquarters, or visit MUST NOT be sufficient alone.
- **FR-011**: NATO Infrastructure and Common Funding MUST cover physical infrastructure projects and their common funding, including pipelines, radar sites, facilities, and comparable shared infrastructure; abstract organizational restructuring MUST NOT qualify.
- **FR-012**: Political Consultation Mechanisms MUST require substantive treatment of how allies coordinate or align policy; meetings, attendance, agendas, minutes headings, scheduling, logistics, distribution, transmittal, or statements that representatives merely discussed an issue MUST NOT qualify alone.
- **FR-013**: Neutral and Non-Aligned Nations MUST remove Norway as a positive example and MUST require substantive discussion of neutrality, non-alignment, Finlandization, or relations with neutral/non-aligned states in the historically relevant period.
- **FR-014**: Neutral and Non-Aligned Nations MUST treat mere mention of Sweden, Finland, Austria, Switzerland, Yugoslavia, or another potentially relevant state as insufficient evidence and MUST explicitly exclude NATO and Warsaw Pact members when the document concerns their ordinary alliance role.
- **FR-015**: Intelligence Sharing MUST require actual or proposed exchange of classified assessments, imagery, warning data, collection results, or governed access among allies; unauthorized disclosure, suspected leaks, press handling, and descriptions of intelligence capability MUST be negative examples rather than positive evidence.
- **FR-016**: Defense Spending MUST require substantive discussion of budgets, expenditure, financial targets, affordability, procurement financing, or economic burden; organizational restructuring without spending discussion MUST NOT qualify.
- **FR-017**: Warsaw Pact MUST distinguish substantive discussion of the alliance, its posture, coordination, structure, or internal dynamics from a passing mention; passing references SHOULD be represented as entities or ordinary tags rather than thematic topics.
- **FR-018**: Every v2 topic MUST contain a precise description, representative positive examples, and representative negative examples that distinguish it from its nearest confusable topics.
- **FR-019**: Every v2 topic MUST follow a universal substantive-subject rule: assign the topic only when it is an important subject of the document, demonstrated through analysis, decision, proposal, recommendation, operational treatment, or sustained description.
- **FR-020**: The universal rule MUST state that a keyword, named entity, country, organization, meeting, citation, document title, distribution-list entry, or single passing reference is insufficient by itself.
- **FR-021**: The universal rule MUST prefer omission over a weak or incidental assignment and MUST allow a document to receive an empty thematic-topic list when no approved topic is substantively supported.
- **FR-022**: Administrative or documentary form—such as agenda, notice, report, corrigendum, cover note, or transmittal—MUST NOT be introduced as a thematic topic; such characteristics remain document-type metadata or ordinary tags.
- **FR-023**: The classifier MUST receive the full v2 category path, category description, topic description, positive examples, and negative examples for every topic.
- **FR-024**: Classification-relevant taxonomy information MUST NOT be silently discarded while preparing the taxonomy for classification.
- **FR-025**: The classifier MUST be instructed to identify all substantively supported topics, but MUST NOT be encouraged to include marginal topics merely to maximize coverage.
- **FR-026**: Every topic assignment MUST include a direct quotation from the document that demonstrates the defining topic relationship, not merely the occurrence of a related word.
- **FR-027**: Each supporting quotation MUST be verified against the document text before the assignment is published as grounded evidence.
- **FR-028**: Quote verification MAY normalize line wrapping, repeated whitespace, and equivalent straight/typographic punctuation, but MUST NOT add, remove, reorder, or replace substantive words.
- **FR-029**: An assignment with unverified quoted evidence MUST be rejected or retried; it MUST NOT be published as a valid grounded topic assignment.
- **FR-030**: The v2 taxonomy MUST document the mapping from every renamed, moved, or split v1 topic path to its v2 destination or destinations.
- **FR-031**: Migration guidance MUST distinguish safe one-to-one path changes from splits that require document reclassification.
- **FR-032**: Existing archives MUST NOT be rewritten automatically merely because the v2 taxonomy becomes available.
- **FR-033**: Taxonomy preparation MUST detect duplicate full topic paths and missing required classification guidance before classification begins.
- **FR-034**: Validation MUST include the known false-positive patterns from the NATO archive review, especially the 85 challenged Extended Deterrence and Tactical Nuclear Sharing assignments and representative failures involving consultation, strike planning, command authority, commands/infrastructure, neutrality, intelligence leaks, and defense spending.
- **FR-035**: Validation MUST include positive examples for each renamed or newly split topic so that reducing false positives does not eliminate legitimate assignments.

### Key Entities

- **Taxonomy Version**: A named, independently selectable set of approved categories and topics with a version-specific file and migration relationship to earlier versions.
- **Category**: A top-level thematic grouping with a name and description that supplies context to its member topics.
- **Topic**: An approved thematic subject with a unique full path, precise description, positive examples, negative examples, and a substantive-evidence threshold.
- **Topic Assignment**: A document-to-topic relationship containing the approved v2 path and a directly quoted justification.
- **Evidence Quotation**: A source passage used to demonstrate why a topic is a substantive subject of the document, with a verification state against the document text.
- **Migration Mapping**: The relationship between a v1 topic path and one or more v2 paths, including whether automatic replacement is safe or reclassification is required.
- **Validation Case**: A reviewed document example with expected included topics, expected excluded topics, and the evidence supporting that expectation.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: At least 90% of topic decisions in a held-out, human-reviewed validation set are accepted as correct, counting both appropriate inclusion and appropriate omission.
- **SC-002**: At least 90% of the 85 previously challenged Extended Deterrence and Tactical Nuclear Sharing cases no longer receive either replacement topic unless the review evidence independently demonstrates the narrower definition.
- **SC-003**: At least 90% of positive validation examples for Extended Nuclear Deterrence, Nuclear Sharing and Forward Deployment, Nuclear Release Authority, Command Structure and Appointments, and NATO Infrastructure and Common Funding receive the expected v2 topic.
- **SC-004**: At least 95% of routine agendas, meeting notices, distribution lists, cover notes, transmittal notes, corrigenda, cancellations, and empty scans without substantive policy content receive no thematic topic.
- **SC-005**: No validation case receives Neutral and Non-Aligned Nations solely because it mentions Norway, Denmark, or another NATO member in its ordinary alliance role.
- **SC-006**: No validation case receives Intelligence Sharing solely because it discusses an unauthorized leak, press disclosure, or adversary intelligence capability.
- **SC-007**: 100% of published topic justifications in the validation run contain a quotation verifiable in the source after only permitted conservative normalization.
- **SC-008**: 100% of v2 topics presented for classification retain their category context, descriptions, positive examples, and negative examples.
- **SC-009**: 100% of renamed, moved, or split v1 topic paths have documented migration guidance, and every split is marked as requiring reclassification.
- **SC-010**: The original taxonomy remains selectable and produces unchanged approved paths when explicitly selected.
- **SC-011**: A taxonomy maintainer can identify the defining inclusion threshold and the most important exclusions for any v2 topic in under two minutes using the taxonomy alone.

## Assumptions

- `NATO_themes_v2.yaml` is opt-in and coexists with the original taxonomy; it does not silently become the default as part of this feature.
- Existing taxonomy consumers continue to use two-part Category/Topic paths. The revised logical hierarchy is expressed through six clearer top-level categories rather than adding an additional path depth.
- Topics not named in the required changes retain their substantive meaning, though they may move to a more appropriate top-level category and receive clearer negative examples.
- Existing archive topic tags are not automatically migrated. Split topics require reclassification because one old assignment may map to neither, either, or both replacement topics.
- Ordinary entities and conceptual tags remain available for meaningful mentions that do not meet the thematic-topic threshold.
- The supplied NATO archive validation feedback is an evaluation source, not production data to be committed to the repository.
- Conservative quote normalization covers presentation differences only; it never permits paraphrases to be presented as direct quotations.
