# Data Model: LLM Topic Extraction (Integrated)

## Entities

### TopicHierarchy (YAML structure)
- **categories**: List of `CategoryDefinition`

### CategoryDefinition
- **category**: String (name)
- **description**: String
- **topics**: List of `TopicDefinition`

### TopicDefinition
- **topic**: String (name)
- **description**: String
- **positive_anchor**: String (optional)
- **negative_anchor**: String (optional)

### CategorySelectionSchema (Pydantic)
- **selected_categories**: List[str]

### TopicSelectionSchema (Pydantic)
- **assignments**: List[TopicAssignment] (max length: 3)

### TopicAssignment (Pydantic)
- **category**: String
- **topic**: String
- **reason**: String (specific, non-generic justification)

## Validation Rules
- `category` and `topic` names used in assignments MUST exist in the provided hierarchy.
- **Strict Limit**: At most 3 `TopicAssignment` entries allowed per document.
- **Reasoning**: `reason` MUST NOT be generic (e.g., MUST avoid "it is the context").
- Tags MUST NOT contain spaces (replaced by hyphens).
- Tags MUST follow `#Category/Topic` structure.
- **Isolation**: Tags are removed from YAML frontmatter and stored exclusively in the Abstract callout.
