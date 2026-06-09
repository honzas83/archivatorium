# Feature Specification: Canonical Tag Data Layer

**Feature Branch**: `023-canonical-tag-layer`

**Created**: 2026-06-09

**Status**: Draft

**Input**: User description: "Create a canonical generated tag data layer for generated OCRPolish Markdown. The system must treat #Entities/..., #Topics/..., and #Tags/... as the authoritative tag syntax. It must parse generated Markdown into a structured model containing conceptual tags, grouped entities, and topics. The parser must normalize tags consistently and deduplicate values. The canonical parsed model must store normalized tag paths without the leading #. Rendering helpers may add # when writing Markdown. The parser should retain enough information to render canonical tags again, but counters, indexing, XLSX, and resume logic should consume the normalized structured model rather than raw Markdown strings. The parser must support entity types State, Org, City, and Person. City tags use the form #Entities/City/<State>/<City>. Topic tags use #Topics/<taxonomy-path>, and conceptual tags use #Tags/<tag>. Malformed generated tags must be ignored with a warning or reported as parse diagnostics; they must not update counters silently. The parser must ignore obsolete unprefixed tags. Legacy tag support is not needed and must not be implemented in the production parser. The system must replace legacy metadata counters with counters derived only from canonical generated tags. Counters must include conceptual tags, topics, and entities grouped by entity type. Counter storage and update logic must be independent of frontmatter metadata schema fields."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Authoritative Tag Parsing (Priority: P1)

As an archivist, I want the system to parse and load tags using only the authoritative prefixes (`#Entities/...`, `#Topics/...`, `#Tags/...`) from processed Markdown files, ignoring legacy or unprefixed tags, so that the index pages, database tables, and Excel reports are built on a consistent and clean taxonomy.

**Why this priority**: Core value of the feature; ensures data cleanliness and consistency across downstream indexing tools.

**Independent Test**: Can be tested by running the parser on a Markdown file containing a mix of canonical tags (e.g. `#Entities/Org/NATO`), legacy tags (e.g. `#Category/Military`), and unprefixed tags (e.g. `#Nuclear-Deterrence`). Only the canonical tags must be parsed into the structured model.

**Acceptance Scenarios**:

1. **Given** a Markdown file containing the tag `#Entities/Org/NATO` and `#Nuclear-Planning`, **When** the file is parsed, **Then** only `Entities/Org/NATO` is added to the structured model, and the unprefixed `#Nuclear-Planning` is completely ignored.
2. **Given** a Markdown file containing duplicates of the same canonical tag (e.g., `#Tags/Tactical-Weapons` multiple times), **When** the file is parsed, **Then** the tag is deduplicated and represented exactly once in the structured model.

---

### User Story 2 - Tag-Based Counter Generation (Priority: P1)

As a database manager, I want document counters (such as occurrences of states, organizations, cities, topics, and conceptual tags) to be compiled purely from the parsed canonical tags rather than frontmatter schema fields, so that the metadata stats accurately reflect what was tagged.

**Why this priority**: Necessary to decouple counter tracking from metadata frontmatter fields, allowing metadata fields to change or be empty without breaking tag tracking.

**Independent Test**: Can be tested by verifying that tag counters for conceptual tags, topics, and entities (grouped by entity type) are updated correctly after parsing a set of files, regardless of whether the frontmatter schema contains fields for those entities.

**Acceptance Scenarios**:

1. **Given** parsed tags containing `Entities/State/France` and `Entities/State/United-States`, **When** state counters are compiled, **Then** the state counter contains France (count: 1) and United States (count: 1).
2. **Given** parsed tags containing entities, topics, and conceptual tags, **When** counters are generated, **Then** the counters are grouped by conceptual tags, topics, and entities (further sub-grouped by entity types: State, Org, City, Person).

---

### User Story 3 - Malformed Tag Detection and Warning (Priority: P2)

As an operator running the OCR processor, I want the tag parser to flag and warn about malformed tags (like `#Entities/City/London` which lacks the state, or invalid entity types) rather than letting them pollute the database counters silently, so that I can identify prompt issues or taxonomy definitions.

**Why this priority**: Essential for pipeline quality control. Silent failures or silent pollution of database counters lead to incorrect indexing.

**Independent Test**: Can be tested by running the parser on a file containing invalid tags (e.g., `#Entities/City/London` or `#Entities/Country/France`) and verifying that warnings/diagnostics are logged and the invalid tags are not counted.

**Acceptance Scenarios**:

1. **Given** a tag `#Entities/City/London` (lacking State), **When** the tag is parsed, **Then** it is ignored, it does not update the City counter, and a warning is logged detailing the malformed tag.
2. **Given** a tag `#Entities/Country/France` (unsupported type 'Country'), **When** the tag is parsed, **Then** it is ignored, it does not update any entity counters, and a warning is logged.

---

### Edge Cases

- **Malformed City Tags**: Tags like `#Entities/City/France` (too few parts) or `#Entities/City/US/New-York/Manhattan` (too many parts). The system must handle these gracefully by ignoring them and reporting warnings.
- **Malformed Entity Tags**: Tags like `#Entities/State` (no name specified) or `#Entities/Person/` (empty trailing name).
- **Incorrect Prefixes**: Tags starting with `#Entity/` (singular) instead of `#Entities/` or `#Tag/` instead of `#Tags/`. These are obsolete/incorrect and must be ignored.
- **Embedded Hash Symbols**: Text containing hashes that are not tags (e.g. code comment `# comment` or markdown headers like `## Header`). These must not be mistakenly parsed as tags.
- **Casing and Characters**: Tags containing spaces or special characters (e.g. `#Tags/Nuclear Planning`). Since Obsidian tags do not allow spaces, these must be treated as invalid or parsed as `#Tags/Nuclear` depending on standard Obsidian boundary rules.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Authoritative tag syntax. The system MUST recognize only tags prefixed with `#Entities/`, `#Topics/`, or `#Tags/` as valid generated tags.
- **FR-002**: Parser output. The parser MUST extract tags from generated Markdown files and return a structured model representing conceptual tags, topics, and entities (grouped by entity type).
- **FR-003**: Consistency and deduplication. The parser MUST normalize tags consistently using standard component normalization (replacing spaces/special chars with hyphens, preserving casing, removing leading hashes) and deduplicate values per file.
- **FR-004**: Entity types support. The parser MUST support exactly four entity types: State, Org, City, and Person.
- **FR-005**: City tag schema. City tags MUST use the three-part form `#Entities/City/<State>/<City>`.
- **FR-006**: Topic tag schema. Topic tags MUST use the hierarchical form `#Topics/<taxonomy-path>`.
- **FR-007**: Conceptual tag schema. Conceptual tags MUST use the form `#Tags/<tag>`.
- **FR-008**: Diagnostic reporting. Any malformed tag encountered during parsing MUST be ignored and reported as a warning or parse diagnostic, and MUST NOT update counters.
- **FR-009**: Obsolete tag exclusion. The parser MUST ignore obsolete unprefixed tags (e.g., `#Nuclear-Deterrence`) and legacy prefixed tags (e.g. `#Category/...` or `#Cat/...`).
- **FR-010**: Canonical parsed model storage. The structured model MUST store normalized tag paths without the leading `#` character (e.g., `Entities/State/United-States`, `Topics/Taxonomy-Path`, `Tags/Conceptual-Tag`).
- **FR-011**: Tag reconstruction capability. The structured model MUST retain enough information (e.g., type/prefix and path) to render canonical tags back to Markdown with their leading `#` when needed.
- **FR-012**: Downstream consumption. All downstream processes, including counters, indexing, XLSX export, and resume logic, MUST consume the normalized structured tag model rather than raw Markdown tag strings or frontmatter schema fields.
- **FR-013**: Counter replacement. Legacy metadata counters MUST be replaced with counters derived exclusively from canonical generated tags.
- **FR-014**: Schema decoupling. Counter storage and update logic MUST be completely independent of frontmatter metadata schema fields.

### Key Entities

- **Canonical Tag Model**: The structured parsed model containing the extracted tags. Key attributes:
  - `conceptual_tags`: List of normalized conceptual tag paths (without `#` prefix, e.g., `Tags/Conceptual-Tag`).
  - `topics`: List of normalized topic paths (without `#` prefix, e.g., `Topics/Taxonomy/Subtopic`).
  - `entities`: Dictionary or list of normalized entity paths grouped by entity type (State, Org, City, Person) (without `#` prefix, e.g., `Entities/State/France`, `Entities/City/United-Kingdom/London`).
- **Tag Counters**: The tracking metrics for tag occurrences across the vault. Attributes:
  - Conceptual tag occurrences (frequency counter).
  - Topic occurrences (frequency counter).
  - Entity occurrences grouped by entity type (State, Org, City, Person) (frequency counters).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of canonical tags (conceptual, topics, entities) present in processed Markdown files are parsed and represented in the structured model.
- **SC-002**: 100% of malformed tags (e.g. `#Entities/City/London` or `#Entities/Country/France`) are detected, skipped, and logged as warnings.
- **SC-003**: 0% of legacy or unprefixed tags (e.g. `#Nuclear-Deterrence`) are included in the parsed structured model or counters.
- **SC-004**: Counters, indexing, XLSX, and resume logic successfully compile values solely from the parsed canonical tag structured model rather than frontmatter schemas.

## Assumptions

- **Vault Structure**: Input Markdown files follow the generated layout where tags are placed in dedicated sections within the abstract callout block or anywhere in the body.
- **Obsidian Compatibility**: The character set of parsed tags follows Obsidian's naming rules (no spaces, only letters, numbers, hyphens, and slashes).
- **Diagnostic Output**: Warnings about malformed tags will be logged via standard Python logging.
