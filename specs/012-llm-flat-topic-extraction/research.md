# Research: LLM Flat Topic Extraction

## Analysis of Existing Implementation

### Topic Hierarchy Structure
The hierarchy is stored in `topics/NATO_themes.yaml` (and similar files) using a nested structure:
- `categories`: List of category objects.
- `category.topics`: List of topic objects.
- `topic.positive_anchor` / `topic.negative_anchor`: Contain the samples the user referred to.

### Current Two-Step Workflow
1. **Pass 1 (Category Selection)**: The LLM receives only category names and descriptions. It selects applicable categories.
2. **Pass 2 (Topic Selection)**: The LLM receives the subset of topics belonging to the selected categories, including their descriptions and anchors. It selects up to 3 topics.

**Issue**: The category selection step is "blind" to the specific anchors of the underlying topics. This can lead to relevant categories being missed if their broad description doesn't perfectly match the document, even if a specific topic's anchor does.

### Proposed Single-Step Workflow
1. **Linearization**: Transform the nested hierarchy into a flat list of items.
   - Format: `Category/Topic` (path-like identifier).
   - Metadata: Include description, positive anchors, and negative anchors for every item.
2. **Single Pass**: Send the entire flattened hierarchy in one LLM call.
3. **Pydantic Mapping**: The LLM will return selected topics using the flat identifiers, which the system will then split back into Category and Topic components to maintain compatibility with existing `TopicAssignment` models.

## Technical Decisions

### 1. Hierarchy Linearization
- **Decision**: Create a `FlatteningService` that converts `dict` (from YAML) into a list of flat topic definitions.
- **Rationale**: Keeps the `TopicExtractor` clean and allows for easy testing of the transformation logic.
- **Format**: YAML-formatted list in the prompt (as selected by the user).

### 2. Prompt Construction
- **Decision**: Use a single structured extraction call using a new Pydantic schema for flat assignments.
- **Rationale**: Minimizes token overhead and reduces the number of LLM calls while ensuring the output remains parseable.

### 3. Response Mapping
- **Decision**: Selected flat topics (e.g., "Doctrine and Strategy/Nuclear Deterrence") will be post-processed to populate the standard `TopicAssignment` model.
- **Rationale**: Ensures downstream consumers (like Obsidian tag formatters) continue to work without modification.

### 4. Token Management
- **Decision**: Implement a "max samples" configuration (FR-006) to truncate anchors if the hierarchy grows too large.
- **Rationale**: Prevents context window overflows for very large hierarchies.

## Alternatives Considered

### JSON Format for Prompt
- **Rejected because**: User explicitly selected YAML for better readability and lower token overhead.

### Multi-step with "Anchor Preview"
- **Rejected because**: Passing anchors in the category step would basically be the same as passing the whole hierarchy, but more complex to implement and manage.

## Dependencies & Best Practices
- **`pyyaml`**: Standard for YAML processing in Python.
- **`pydantic`**: Use for structured output validation (existing practice in project).
- **`ollama`**: Current client used for LLM interaction.
