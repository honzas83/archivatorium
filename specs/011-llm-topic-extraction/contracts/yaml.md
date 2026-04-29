# YAML Contract: Topic Hierarchy

## Structure

The YAML file MUST follow this structure:

```yaml
categories:
  - category: "Category Name"
    description: "Brief description for the LLM"
    topics:
      - topic: "Topic Name"
        description: "Brief description for the LLM"
        positive_anchor: "Context where this topic applies" (optional)
        negative_anchor: "Context where this topic does NOT apply" (optional)
```

### Constraints
- `category` names SHOULD be unique.
- `topic` names within a category SHOULD be unique.
- Descriptions and anchors are used to build the LLM prompts.
