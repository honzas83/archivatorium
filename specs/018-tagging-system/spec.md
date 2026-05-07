# Feature Specification: Precision Tagging System

**Feature Branch**: `018-tagging-system`  
**Created**: 2026-05-07  
**Status**: Draft  
**Input**: Precision Tagging System Requirements

## User Scenarios & Testing

### User Story 1 - Multi-Output Tagging (Priority: P1)

As an archivist, I want the system to generate three distinct types of tags (conceptual, entity, and taxonomy topics) so that I can perform multi-faceted retrieval across the NATO archive.

**Acceptance Scenarios**:
1. **Given** a document about nuclear deterrence, **When** processed, **Then** it produces:
    - Up to 10 flat conceptual tags (e.g., `#NuclearDeterrence`).
    - Hierarchical entity tags (e.g., `State/USA`, `Org/NATO`).
    - Up to 5 hierarchical topic tags from the taxonomy (e.g., `Category/Doctrine and Strategy/Nuclear Deterrence`).

---

### User Story 2 - Tag Canonicalization and Noise Reduction (Priority: P1)

As a system, I want to filter out OCR noise, merge variants, and reuse existing tags so that the tag vocabulary remains stable and compact.

**Acceptance Scenarios**:
1. **Given** a document with "WINTEX 71" and "Wintex-71", **When** processed, **Then** both are normalized to a single canonical tag `#WINTEX/71`.
2. **Given** a routine meeting agenda, **When** processed, **Then** labels like "agenda" or "notice" are rejected from conceptual tags.
3. **Given** a tag like "Nucl. Deterrence" (OCR error), **When** processed, **Then** it is corrected to the canonical `#NuclearDeterrence` found in `USEFUL_TAGS.yaml`.

---

### User Story 3 - Duplicate Suppression (Priority: P2)

As a system, I want to ensure conceptual tags do not duplicate information already present in entity or topic tags, to avoid redundant indexing.

**Acceptance Scenarios**:
1. **Given** a document where `Org/NATO` is an entity tag, **When** generating conceptual tags, **Then** "NATO" is excluded from the flat tag list.
2. Given a topic tag Category/Military Operations and Capabilities/Military Interoperability, When generating conceptual tags, Then "interoperability" is excluded if it doesn't add distinct conceptual value.

## Clarifications

### Session 2026-05-07
- Q: How should the system handle potential duplicates between conceptual tags and entity/topic tags? → A: Automatic Strict: Always suppress a flat tag if the exact string or canonical form exists in Entity or Topic tags.
- Q: How should the system handle cases where the LLM returns more than the specified maximum number of tags? → A: Prompt Enforced: Take all tags returned by the LLM, restricting them only through prompt instructions.
- Q: How should mentioned cities be stored in the final output? → A: Hierarchical: Store as `City/State/CityName` (matching the entity tag format).
- Q: How should the document be processed for tagging (Entities, Topics, Conceptual)? → A: Second Pass / Whole Document: Process the entire document in a second pass (after primary metadata extraction) using a non-thinking model configuration (`think: false`).
- Q: How should the system handle documents that exceed the LLM's context window for the tagging pass? → A: Sliding Window: Process the document in overlapping chunks and aggregate/deduplicate tags from all windows.
- Q: How should the 32k context window of gemma4:31b affect the processing strategy? → A: Dynamic: Use a single pass for documents < 32k tokens; fallback to sliding window if > 32k.

## Requirements

### Functional Requirements

- **FR-001: Processing Workflow**:
    - **Step 1 (First Chunk)**: Extract primary metadata (Title, Summary, Abstract, Date, Archive Code) from the first 10k tokens.
    - **Step 2 (Tagging Pass)**: Process the document using a non-thinking model configuration (`think: false`):
        - **Dynamic Execution**: If the document is within the model's context window (e.g., 32k tokens), perform a single pass.
        - **Sliding Window Fallback**: For documents exceeding the context window, use a sliding window approach with overlapping chunks.
        - Aggregate and deduplicate tags across all chunks (if multi-pass).
        - Derivation Order (per chunk/pass):
            1. Extract Entities (State, Org, City, Person).
            2. Extract Taxonomy Topics (using `NATO_themes.yaml`).
            3. Extract Conceptual Tags (using `USEFUL_TAGS.yaml` as primary source).
            4. **Strict Suppression**: Always suppress a flat tag if the exact string or canonical form exists in Entity or Topic tags.

- **FR-002: Output Formats**:
    - **Conceptual Tags**: Flat tags (e.g., `#Tag`). Count is determined by the LLM (suggested limit 15 in prompt, but flexible). MUST include all all-caps abbreviations (e.g., `SACEUR`, `SACLANT`).
    - **Entity Tags**: Hierarchical (e.g., `State/Name`, `Org/Name`, `City/State/City`, `Person/Name`).
    - **Topic Tags**: Hierarchical (e.g., `Category/CategoryName/TopicName`). Max 10 (prompt-enforced). Each topic MUST include a brief 'reason' for its assignment, which is displayed in the final document callout.

- **FR-003: Conceptual Tag Inclusion Criteria**:
    - Must represent archivally substantive concepts.
    - Must be present in `USEFUL_TAGS.yaml` OR be a highly meaningful new concept that follows normalization rules.
    - Zero tags are allowed if no meaningful ones are justified.

- **FR-004: Conceptual Tag Exclusion Criteria**:
    - Reject OCR-corrupted or low-signal strings.
    - Reject generic/weak labels (e.g., "document", "file", "text").
    - Reject document-form labels: `report`, `study`, `agenda`, `notice`, `corrigendum`, `working paper`, `communiqué`.
    - **Strict Suppression**: Always suppress a flat tag if the exact string or canonical form exists in Entity or Topic tags.

- **FR-005: Canonicalization and Merge Rules**:
    - Merge aliases and spelling variants.
    - Normalize singular/plural (prefer singular unless plural is a standard term).
    - **Exercise Normalization**: `ExerciseName/YY` (e.g., `WINTEX/71`).

- **FR-006: Taxonomy Topic Filtering**:
    - Apply conservative assignment (high confidence).
    - Strong filtering against routine administrative documents (agendas, scheduling, logistics).

### Supporting Files (Normative)
- `@topics/NATO_themes.yaml`: The source of truth for categories and topics.
- `@topics/USEFUL_TAGS.yaml`: The primary source for conceptual tag reuse.

- **FR-007: Obsidian-Safe Normalization**:
    - ALL tags (Conceptual, Entity, and Topic) MUST be normalized to be Obsidian-safe.
    - **Hyphenation**: Spaces and non-alphanumeric characters (excluding slashes) are replaced with hyphens (`-`).
    - **Casing**: Original casing is preserved.
    - **Consistency**: Taxonomy categories/topics and preloaded useful tags are preprocessed using the same normalization logic.
    - Hierarchical paths must maintain the nesting structure via slashes (e.g., `Category/Doctrine-and-Strategy/Nuclear-Deterrence`).

- **FR-008: Callout Structure**:
    - The abstract callout block MUST follow this order and format:
        1. `# Title`
        2. `Abstract text`
        3. `## Categories/Topics` (Bullet list: `- #[Topic] — [Reason]`)
        4. `## Mentioned Entities` (Bullet list: `- #[Entity]`)
        5. `## Tags` (Flat list of hashtags)

- **FR-009: Entity Context (Feedback Loop)**:
    - The system MUST maintain counters for mentioned states, organisations, and cities across processed documents.
    - The top 20 most frequent entities in each category MUST be injected into the tagging prompt for subsequent documents to ensure naming consistency.

## Success Criteria

- **SC-001**: Tag explosion is controlled (conceptual count is determined by LLM relevance, topics < 10).
- **SC-002**: 100% of entity tags follow the `Type/Name` or `City/State/City` hierarchy.
- **SC-003**: 0% overlap between conceptual tags and entity/topic tags in a sample set.
- **SC-004**: WINTEX/FALLEX exercises are correctly normalized into the hierarchical year form.
- **SC-005**: 100% of tags are Obsidian-safe (no spaces or illegal characters).
