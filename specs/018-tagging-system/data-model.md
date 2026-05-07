# Data Model: Precision Tagging System

## Tagging Pass Result (Single Pass or Window)
This structure represents the raw output from the LLM for a single chunk or the entire document (if in single-pass mode).

```python
class WindowTaggingResult(BaseModel):
    conceptual_tags: List[str]  # Raw list from LLM
    entity_tags: List[str]      # Hierarchical tags: State/X, Org/X, etc.
    topic_tags: List[TopicResult] # Hierarchical tags with reasons
```

## Aggregated Tagging Result (Full Document)
This structure represents the final, deduplicated, and suppressed result for the entire document, regardless of whether it was processed in one pass or multiple windows.

```python
class AggregatedTaggingResult(BaseModel):
    conceptual_tags: List[str]  # Top 15 frequency-weighted, suppressed
    entity_tags: List[str]      # Set union of all extracted entities
    topic_tags: List[TopicResult] # Set union of all extracted topics
```

## Entity Tag Formats
- `State/<Name>` (e.g., `State/United Kingdom`)
- `Org/<Name>` (e.g., `Org/NATO`)
- `City/<State>/<City>` (e.g., `City/USA/Washington`)
- `Person/<Name>` (e.g., `Person/Joseph Luns`)

## Topic Tag Format
- `Category/<CategoryName>/<TopicName>` (e.g., `Category/Doctrine and Strategy/Nuclear Deterrence`)

## Conceptual Tag Format
- `#<CanonicalName>` (e.g., `#StrategicDeterrence`)
- Exercises: `#<Name>/<YY>` (e.g., `#WINTEX/71`)
