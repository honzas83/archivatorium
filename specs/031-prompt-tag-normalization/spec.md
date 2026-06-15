# Feature Specification: Prompt Tag Normalization

**Feature Branch**: `031-prompt-tag-normalization`

**Created**: 2026-06-12

**Status**: Draft

**Input**: User description: "In this enhancement, we will modify ONLY the prompt. After processing data sample, we got COUNTS_v6.csv and docs/tag_analysis_report.md . Use the findings for the specification"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Normalize Repeated Entities (Priority: P1)

As an archive curator reviewing generated metadata, I need the extraction instructions to prefer one canonical representation for the same real-world entity so that repeated organisations, states, and cities are not split across casing, language, or spelling variants.

**Why this priority**: The analysis found 1,374 unique entity values with 970 single-occurrence entities, indicating that entity fragmentation is the largest source of vocabulary noise.

**Independent Test**: Run the tagging flow on sample excerpts containing known variants such as NATO/nato/OTAN, Bruxelles/Brussels, Allemagne/Germany, and USA/United States; the resulting entity tags use the canonical English/title-case form.

**Acceptance Scenarios**:

1. **Given** a French excerpt mentioning "Bruxelles" and "Allemagne", **When** metadata is generated, **Then** the entity tags use `City/Belgium/Brussels` and `State/Germany`.
2. **Given** an excerpt mentioning "nato", "OTAN", or "Organisation du Traite de l'Atlantique Nord", **When** metadata is generated, **Then** the organisation entity uses `Org/NATO`.
3. **Given** an excerpt mentioning "USA", "usa", or "United States", **When** metadata is generated, **Then** the state entity uses `State/United-States`.

---

### User Story 2 - Recover Obvious OCR-Damaged Entities (Priority: P2)

As a researcher searching across OCR-derived metadata, I need obvious OCR damage in entity names to be corrected during extraction so that corrupted one-off names do not become permanent vocabulary entries.

**Why this priority**: The analysis found multiple single-occurrence corrupted forms of high-frequency entities, especially variants of recurring organisation names caused by OCR damage such as split words, missing letters, and punctuation substitutions.

**Independent Test**: Run the tagging flow on excerpts containing OCR-damaged variants of known entities; the generated metadata uses the recognizable standard entity rather than preserving the damaged spelling.

**Acceptance Scenarios**:

1. **Given** an excerpt containing an obviously OCR-damaged variant of a known recurring organisation name, **When** metadata is generated, **Then** the entity tag resolves to the standard organisation entity form.
2. **Given** an excerpt containing a clear OCR misspelling of a known place or organisation, **When** the surrounding context makes the intended entity unambiguous, **Then** the generated entity uses the corrected standard name.
3. **Given** an OCR-damaged string whose intended entity is ambiguous, **When** metadata is generated, **Then** no invented canonical entity is created from the damaged text.

---

### User Story 3 - Preserve Useful Substantive Tags While Reducing Noise (Priority: P3)

As a metadata maintainer, I need the prompt update to reduce duplicate and malformed tags without suppressing justified substantive concepts, topics, acronyms, and archival terms.

**Why this priority**: The sample contains 518 unique conceptual tags, with 282 appearing only once; some one-off values are noise, while others are legitimate rare concepts that should remain when clearly justified.

**Independent Test**: Run the tagging flow on excerpts containing both common abbreviations and rare substantive terms; common abbreviations remain available when meaningful, while duplicate casing, punctuation, and spelling variants are reduced.

**Acceptance Scenarios**:

1. **Given** an excerpt with meaningful all-caps acronyms such as NATO, SHAPE, SACLANT, or DPC, **When** metadata is generated, **Then** those acronyms are preserved where they are justified by the text.
2. **Given** an excerpt with a non-acronym written in all caps, **When** metadata is generated, **Then** the tag uses a normal title-cased form rather than preserving shouting case.
3. **Given** an excerpt with a substantive but rare archival concept, **When** the concept is clearly supported by the text, **Then** the concept remains eligible for tagging even if it is not frequent in the sample.
4. **Given** an excerpt or filename contains both an acronym and its expanded form for the same concept, **When** metadata is generated, **Then** conceptual tags include only one canonical form, preferring the standard acronym for well-known domain terms.

---

### User Story 4 - Use Relative Filename Context (Priority: P4)

As an archive curator processing files whose paths contain archival codes, folder structure, document year, or other contextual metadata, I need the tagging prompt to include the full source-relative filename so the LLM can condition tag choices on that context when the document text is incomplete or ambiguous.

**Why this priority**: Archival filenames and relative paths often encode collection structure, years, document identifiers, and series-level context that may not be repeated in OCR text.

**Independent Test**: Inspect a generated tagging prompt for a nested input document and verify it includes the full path relative to the input directory, including subdirectories and filename.

**Acceptance Scenarios**:

1. **Given** an input file at `Collection-Series/1974/ORG-DOCUMENT-1974-05.md`, **When** metadata tagging is requested, **Then** the tagging prompt includes that full relative filename before the full document text.
2. **Given** a relative filename containing an archival code or year, **When** metadata tagging is requested, **Then** the prompt tells the LLM it may use that filename as contextual evidence for archival code, date/year, series, or collection context.
3. **Given** filename context and document text disagree, **When** metadata tagging is requested, **Then** the prompt tells the LLM not to let the filename override clearly contradictory document text.

### Edge Cases

- The prompt-only enhancement must not change file processing, metadata storage, taxonomy files, report generation, command options, or non-prompt behavior.
- Passing the relative filename into the prompt may require minimal prompt-context plumbing, but it must not change output schemas, CLI options, taxonomy files, useful-tags files, parser behavior, or post-processing behavior.
- City tags must preserve the expected hierarchy of country then city; region names, states, or countries must not be emitted as cities.
- Country and organisation names that appear in French or alternate abbreviations must be normalized to the selected English canonical form when the intended entity is clear.
- Acronyms must remain all caps only when they are standard abbreviations; ordinary words in all caps must be normalized.
- Conceptual tags must strictly exclude entities: once an organisation, state, city, or person is represented in `entity_tags`, its exact name, aliases, acronyms, translated forms, expanded names, punctuation/case variants, hyphenation variants, and compacted normalized variants must be forbidden from `conceptual_tags`.
- Conceptual tags must not include both an acronym and expanded full-name form for the same concept when a canonical choice is clear.
- The tagging prompt and structured LLM schema must present categories in decoding order: Categories/Topics first, Entities second, and Tags last.
- Topic extraction must remain mandatory and multi-label: the model must review the full approved taxonomy and emit all supported Category/Topic entries with quoted evidence, not just the single best or most obvious topic, using an empty `topic_tags` list only when no approved taxonomy topic is supported.
- Diacritics and accents in entity names must not create separate vocabulary entries from the same English entity.
- OCR recovery must be conservative: obvious damage may be corrected, but unclear names must not be guessed into unrelated entities.
- Filename context must be treated as a contextual hint, not as a replacement for direct evidence from the full document text.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The enhancement MUST be limited to the tagging prompt or its prompt text; it MUST NOT change processing flow, output formats, schemas, taxonomy files, data files, command options, or post-processing behavior.
- **FR-002**: The prompt MUST instruct metadata generation to normalize entity names for states, organisations, and cities into a consistent English canonical form when a clear equivalent exists.
- **FR-003**: The prompt MUST instruct metadata generation to use consistent title casing for state, city, person, and organisation names, while preserving all-caps only for standard acronyms.
- **FR-004**: The prompt MUST instruct metadata generation to correct obvious OCR corruption in entity names when context clearly identifies the intended entity.
- **FR-005**: The prompt MUST instruct metadata generation to avoid creating entity tags from ambiguous OCR-damaged strings when the intended entity cannot be reliably determined.
- **FR-006**: The prompt MUST instruct metadata generation to use the expected entity hierarchy formats: `State/<name>`, `Org/<name>`, `City/<country>/<city>`, and `Person/<name>`.
- **FR-007**: The prompt MUST explicitly address high-impact fragmentation patterns found in the sample: case mismatches, French-English duplicates, alternate country keys, city/country structural confusion, and OCR-corrupted entity variants.
- **FR-008**: The prompt MUST preserve justified topic selection behavior, including the requirement that topic reasons include direct textual evidence.
- **FR-009**: The prompt MUST preserve justified conceptual tagging behavior, including reuse of known vocabularies and inclusion of meaningful acronyms when supported by the source text.
- **FR-010**: The prompt MUST include enough concrete examples or rules for a reviewer to verify expected outcomes for NATO/OTAN, Brussels/Bruxelles, Germany/Allemagne, United States/USA, and obvious OCR-damaged recurring-organisation variants.
- **FR-011**: The prompt MUST include the full source-relative filename for each document when that filename is available.
- **FR-012**: The prompt MUST instruct metadata generation that the relative filename can inform archival code, document year/date, series, collection, and other metadata context when consistent with the full document text.
- **FR-013**: The prompt MUST instruct metadata generation not to let filename context override clearly contradictory document text.
- **FR-014**: The prompt MUST instruct metadata generation not to emit both an abbreviation and its expanded full-name form as conceptual tags when both refer to the same concept.
- **FR-015**: The prompt MUST instruct metadata generation to prefer the standard acronym as the canonical conceptual tag for well-known NATO-domain terms when choosing between an acronym and expanded form.
- **FR-016**: The prompt MUST instruct metadata generation to apply strict entity/tag separation: after choosing `entity_tags`, the model must treat each entity name and normalized variant as forbidden for `conceptual_tags`, including aliases, acronyms, translated forms, expanded names, punctuation/case variants, hyphenation variants, and compacted forms.
- **FR-017**: The prompt MUST instruct metadata generation to include a conceptual tag related to an entity only when it adds substantive archival meaning beyond the entity itself.
- **FR-018**: The tagging prompt and structured LLM response schema MUST present tag categories in this order for model decoding: `topic_tags` for Categories/Topics, then `entity_tags` for Entities, then `conceptual_tags` for Tags.
- **FR-019**: The prompt and structured LLM response schema descriptions MUST prevent topic omission by describing `topic_tags` as a mandatory multi-label taxonomy classification step for substantive archival text, with `[]` allowed only when no approved taxonomy topic is clearly supported.
- **FR-021**: The prompt MUST instruct metadata generation to detect all matching approved taxonomy topics, including multiple topics across different categories, rather than selecting only the single best or most obvious topic.
- **FR-020**: The configured minimum number of conceptual tags for substantive documents MUST be relaxed to 1, while still requiring every clearly justified useful conceptual tag and imposing no hard maximum.

### Key Entities *(include if feature involves data)*

- **Entity Tag**: A hierarchical metadata value representing a real-world state, organisation, city, or person mentioned in source text.
- **Topic Tag**: A taxonomy-backed subject classification selected only when clearly justified by the source text and accompanied by textual evidence.
- **Conceptual Tag**: A substantive archival concept or acronym that supports discovery but is not merely a duplicate of an entity or topic component.
- **Semantic Duplicate Conceptual Tag**: Two conceptual tags that refer to the same concept despite different surface forms, such as an acronym form and an expanded-name form for the same concept.
- **Entity-Duplicate Conceptual Tag**: A forbidden conceptual tag that repeats an entity tag using the same name, alias, acronym, translation, expanded-name variant, punctuation/case variant, hyphenation variant, or compacted normalized form.
- **Canonical Form**: The preferred spelling, language, hierarchy, and casing used to represent a real-world entity consistently across documents.
- **Sample Finding**: An observed vocabulary-quality issue from the processed data sample, including counts, duplicate examples, OCR damage, multilingual variants, and hierarchy errors.
- **Relative Filename**: The source document path relative to the input directory, including subdirectories and the filename, used as prompt context for archival codes, years, and collection structure.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On the analyzed sample patterns, known duplicates for NATO/OTAN/nato, Brussels/Bruxelles, Germany/Allemagne, United States/USA, and obvious OCR-damaged recurring-organisation variants resolve to a single intended canonical entity in at least 90% of clear cases.
- **SC-002**: In a validation sample, lowercase entity variants for high-frequency organisations and states decrease by at least 80% compared with the v6 sample findings.
- **SC-003**: In a validation sample, French-English duplicate entity pairs listed in the analysis report decrease by at least 80% where the English equivalent is clear.
- **SC-004**: In a validation sample, obvious OCR-corrupted entity variants for high-frequency entities decrease by at least 75% without creating unrelated replacement entities.
- **SC-005**: Topic tag coverage and evidence quality remain stable: at least 95% of sampled topic selections include a direct source-text citation and no material drop in clearly justified topic selection is observed.
- **SC-006**: Reviewers can validate the enhancement by inspecting only generated metadata and the updated prompt; no additional data migration or manual cleanup is required to assess whether the prompt change works.
- **SC-007**: For every processed document with a known input directory, reviewers can inspect the tagging prompt and see the exact source-relative filename before the full document text.
- **SC-008**: In a validation sample containing abbreviation/full-name pairs for the same concept, reviewers observe only one canonical conceptual tag for each pair in at least 90% of clear cases.
- **SC-009**: In a validation sample containing clearly extracted entities, reviewers observe no matching conceptual tags for the same organisations, states, cities, or persons in at least 90% of clear cases unless the conceptual tag adds distinct substantive meaning.
- **SC-010**: Prompt and schema inspection show `topic_tags` before `entity_tags` before `conceptual_tags`, matching Categories/Topics, Entities, then Tags.
- **SC-011**: Prompt and schema inspection show a single topic-section instruction to detect all matching approved taxonomy topics with quoted evidence, including multiple topics across categories when justified.

## Assumptions

- The prompt change will be evaluated against representative excerpts from the same data source used to produce `COUNTS_v6.csv` and `docs/tag_analysis_report.md`.
- English canonical forms are preferred for states, cities, and organisations because the analysis shows multilingual duplicates fragment search and review.
- The approved taxonomy and useful vocabulary remain unchanged for this enhancement.
- Existing output consumers expect the same metadata categories and hierarchical formats, so compatibility is more important than introducing a new normalization layer.
- Rare tags are not automatically wrong; the prompt should reduce malformed duplicates while retaining rare concepts that are clearly supported by the text.
- Relative filenames are available during normal CLI-driven metadata processing because each input file is processed under a known input directory; direct programmatic callers without an input directory may fall back to the filename only.
