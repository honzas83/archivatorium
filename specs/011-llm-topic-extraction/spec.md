# Feature Specification: LLM Topic Extraction

**Feature Branch**: `011-llm-topic-extraction`  
**Created**: 2026-04-29  
**Status**: Draft  
**Input**: User description: "In this specification, we will focus on additional LLM calls after metadata extraction. We will implement two-step topic extraction. Our topic hierarchy is specified in @topics/NATO_themes.yaml , but we can use any other YAML with a similar structure. The assigned topics will be used added into the Abstract callout section as tags (https://obsidian.md/help/tags), use hierarchical tags. Use hyphens as replacement for spaces."

## Clarifications

### Session 2026-04-29
- Q: Should the new hierarchical tags coexist with the existing flat frontmatter tags, or should they replace them entirely when a hierarchy is provided? → A: **Callout Only**: Remove tags from YAML frontmatter property. Place hierarchical topics and flat tags in dedicated sections within the "Abstract" callout.
- Q: Should the topic extraction use the full document text as context, or the newly extracted (and much shorter) abstract? → A: **Raw Text Only**: Use up to 10kB of raw document text (first chunk). Do NOT pass extracted metadata (abstract/summary) to avoid hallucinations.
- Q: How many topics should be assigned? → A: **Limit to 3**: Select at most 3 most important topics. This is enforced in the schema.
- Q: What information should be provided for each topic? → A: **Topic + Reasoning**: Provide the hierarchical tag and a specific, non-generic reason why it was selected.
- Q: How should topics be formatted in the callout? → A: **List**: One topic per line: `#Category/Topic — Reason`.
- Q: How should flat tags be formatted? → A: **Inline**: Flat tags remain on a single line in their own section.
- Q: Should the model always use all 3 slots? → A: **No**: Quality over quantity. Use fewer topics if they don't truly fit, especially for short documents (< 3 pages).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Two-Step Topic Extraction (Priority: P1)

The user wants the system to automatically categorize documents into a predefined topic hierarchy using a two-step LLM process. The first step identifies high-level categories, and the second step selects specific topics within those categories. To ensure maximum accuracy and avoid hallucinations, the LLM uses only a significant portion (up to 10kB) of the raw document text as context.

**Why this priority**: This is the core logic requested for the feature.

**Independent Test**: Can be tested by providing a document and the `NATO_themes.yaml` file, then verifying that the LLM output follows the category-then-topic flow and matches the hierarchy.

**Acceptance Scenarios**:

1. **Given** a document and a YAML topic hierarchy, **When** the extraction process is run, **Then** the system first prompts the LLM to select applicable categories from the YAML using only raw text as context.
2. **Given** selected categories, **When** the second LLM call is made, **Then** the LLM selects at most 3 specific sub-topics and provides a specific reasoning for each.

---

### User Story 2 - Obsidian Hierarchical Tagging (Priority: P1)

The user wants the assigned topics to be represented as hierarchical tags in their Obsidian vault, including justifications. The tags should reflect the category/topic relationship and be formatted as a list within the document body.

**Why this priority**: Required for the output to be useful and interpretable in the target environment (Obsidian).

**Independent Test**: Verify that the generated tags use the `#Parent/Child — Reasoning` format and that all spaces in tags are replaced with hyphens.

**Acceptance Scenarios**:

1. **Given** a category "Doctrine and Strategy" and a topic "Nuclear Deterrence", **When** the tag is generated, **Then** it must be `#Doctrine-and-Strategy/Nuclear-Deterrence — [Specific Reason]`.
2. **Given** any topic or category name with spaces, **When** processed, **Then** all spaces are replaced with hyphens in the final tag.

---

### User Story 3 - Metadata Integration in Abstract Section (Priority: P2)

The user wants the extracted topic tags and flat tags to be organized into dedicated sections within the "Abstract" callout section, rather than in the YAML frontmatter.

**Why this priority**: Ensures the metadata is organized and presented as specified by the user for optimal Obsidian display.

**Independent Test**: Run the `metadata` command with a hierarchy file provided and check the resulting Markdown file to ensure tags are removed from frontmatter and placed in the Abstract section with headers `## Categories/Topics` and `## Tags`.

**Acceptance Scenarios**:

1. **Given** the `metadata` command is run with a hierarchy file, **When** topics are extracted, **Then** they are added to the Abstract callout in a list format, and flat tags are added inline under their own header.
2. **Given** no hierarchy file is provided, **When** the `metadata` command is run, **Then** it proceeds with standard metadata extraction, but still moves flat tags to the Abstract callout.

### Edge Cases

- **Missing Hierarchy**: How should the system behave if the specified YAML file is missing or invalid? (Requirement: Fall back to standard metadata extraction).
- **No Match Found**: What if the LLM determines that none of the topics in the hierarchy apply to the document? (Requirement: Proceed with metadata extraction without adding topic tags).
- **Ambiguous Documents**: How does the system handle documents that could belong to multiple categories? (Requirement: Support multiple categories and topics, up to 3).
- **Short Documents**: How should the system handle very short documents? (Requirement: Be more selective; do not feel forced to fill 3 slots if only one fits).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST perform topic extraction using exactly two sequential LLM calls (1: Category selection, 2: Topic selection).
- **FR-002**: System MUST integrate topic extraction as an optional enhancement to the `metadata` command.
- **FR-003**: System MUST load the topic hierarchy from a YAML file (e.g., `topics/NATO_themes.yaml`) when a hierarchy path is provided to the `metadata` command.
- **FR-004**: System MUST format output as hierarchical tags using the `#Category/Topic` syntax.
- **FR-005**: System MUST replace all spaces in category and topic names with hyphens (`-`) for tag generation.
- **FR-006**: System MUST append the generated hierarchical tags and reasoning to the "Abstract" callout section as a list (one per line).
- **FR-007**: System MUST append flat tags to the "Abstract" callout section in an inline format.
- **FR-008**: System MUST NOT include tags in the YAML frontmatter property when this pass is active.
- **FR-009**: System MUST use only a significant portion of the raw document text (up to 10kB) as context for topic extraction, avoiding hallucinations from other extracted metadata.
- **FR-010**: System MUST enforce a strict limit of at most 3 topics per document in the schema.
- **FR-011**: System MUST require a specific, non-generic reasoning for each topic assignment.
- **FR-012**: System MUST NOT introduce a new top-level subcommand for topics.

### Key Entities *(include if feature involves data)*

- **Topic Hierarchy**: A YAML-defined structure containing `categories` and their nested `topics`.
- **Hierarchical Tag**: A string representation of a category-topic pair formatted as `#Category-Name/Topic-Name`.
- **Abstract Callout**: A specific section in the document body (Obsidian callout) with `## Categories/Topics` and `## Tags` subheaders.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of successfully processed documents contain hierarchical tags that exactly match the provided YAML hierarchy.
- **SC-002**: All generated tags are valid Obsidian tags (no spaces, starts with `#`, hierarchical structure).
- **SC-003**: Topic extraction time for a standard document is within reasonable LLM latency limits.
- **SC-004**: The resulting Markdown file remains valid and correctly formatted for Obsidian display.
- **SC-005**: Reasoning provided is specific to the document content (no generic filler).
