# Research: LLM Topic Extraction (Integrated)

## Decision 1: Context for Topic Extraction
**Decision**: Use ONLY the first 10kB chunk of raw document text as context for the two-step extraction process. Do NOT use extracted metadata (abstract/summary).
**Rationale**: Prevents hallucinations by grounding the LLM strictly in the source text. 10kB provides sufficient context for high-precision categorization.
**Alternatives considered**: Using both abstract and text (hallucination risk).

## Decision 2: Integration Point
**Decision**: Integrate the `TopicExtractor` service into the `MetadataProcessor.process_file` method.
**Rationale**: Unified pass avoids redundant document understanding and simplifies the CLI.
**Alternatives considered**: Standalone command (rejected by user).

## Decision 3: Tag Isolation (No Duplication)
**Decision**: Store all tags (hierarchical topics and flat tags) exclusively in the `[!abstract]` callout section. Remove them from the YAML frontmatter.
**Rationale**: Keeps the frontmatter clean and presents metadata in a structured, readable way within the Obsidian body.
**Alternatives considered**: Duplication in frontmatter (rejected by user).

## Decision 4: Formatting and Reasoning
**Decision**: Format hierarchical topics as a list with reasoning (`#Category/Topic — Reason`) and flat tags inline.
**Rationale**: Improves transparency and searchability in Obsidian. Mandatory reasoning forces the LLM to provide evidence-based assignments.

## Decision 5: Selectivity and Limits
**Decision**: Enforce a strict limit of 3 topics in the schema and instruct the LLM to use fewer if they don't fit (especially for short docs).
**Rationale**: Prevents "over-tagging" and ensures only high-confidence matches are assigned.

## Research Findings

### Prompt Integration
The `TopicExtractor` is invoked after the primary metadata pass. It uses the same `first_chunk` (now expanded to 10kB) that the `MetadataProcessor` already reads.

### Obsidian Tag Syntax
Obsidian tags must not contain spaces.
Hierarchical tags use the `#Parent/Child` format.
Implementation: `f"#{category.strip().replace(' ', '-')}/{topic.strip().replace(' ', '-')}"`.

### MetadataProcessor Workflow
1. Extract primary metadata (Title, Summary, Abstract, etc.).
2. If `hierarchy_file` is provided:
    a. Invoke `TopicExtractor.extract_topics(first_chunk)`.
    b. Step 1: Category selection.
    c. Step 2: Topic selection (max 3) + specific reasoning.
3. Rework Callout:
    a. Move title and abstract to body callout.
    b. Remove `tags` from frontmatter dictionary.
    c. Add `## Categories/Topics` section with list of topics and reasons.
    d. Add `## Tags` section with inline flat tags.
4. Write final Markdown.
