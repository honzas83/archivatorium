# Data Model: LLM Flat Topic Extraction

## Entities

### Topic (Flat)
Represents a linearized topic for LLM consumption.
- `id`: String (Format: "Category/Topic")
- `description`: String
- `positive_samples`: List[String]
- `negative_samples`: List[String]

### FlatHierarchy
The collection of all topics prepared for the prompt.
- `topics`: List[Topic (Flat)]

## Pydantic Schemas

### FlatTopicAssignment
The model returned by the LLM in a single pass.
- `topic_id`: String (Must match an ID from the provided hierarchy)
- `reason`: String (Justification based on text)

### FlatTopicSelectionSchema
Container for the LLM response.
- `assignments`: List[FlatTopicAssignment] (Max 3)

## Mapping to Existing Model
After extraction, `FlatTopicAssignment` is mapped to the existing `TopicAssignment`:
- `category`: Extracted from `topic_id` (part before first "/")
- `topic`: Extracted from `topic_id` (part after first "/")
- `reason`: Passed through
