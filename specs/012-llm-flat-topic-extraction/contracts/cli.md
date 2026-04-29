# CLI Contract: Flat Topic Extraction

The `ocrpolish` CLI is updated to support an optional flag to toggle between the legacy two-step extraction and the new single-step flat extraction.

## New Arguments

- `--flat-topics`: (Optional) Boolean flag. When set, uses the single-step flat extraction method.

## Usage Example

```bash
ocrpolish input_dir output_dir --hierarchy-file topics/NATO_themes.yaml --flat-topics
```

## Behavior

1. If `--hierarchy-file` is provided:
   - If `--flat-topics` is NOT set: Perform legacy two-step (Category -> Topic) extraction.
   - If `--flat-topics` IS set:
     - Load YAML hierarchy.
     - Flatten into `Category/Topic` list.
     - Send single request to LLM with flattened YAML (including all samples).
     - Parse response and map back to `Category/Topic` tags.
2. If `--hierarchy-file` is NOT provided: Skip topic extraction.
