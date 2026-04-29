# Quickstart: Flat Topic Extraction

## Setup

1. Ensure you have a YAML hierarchy file in `topics/` (e.g., `NATO_themes.yaml`).
2. Verify your LLM (Ollama) is running and accessible.

## Execution

To run topic extraction using the new single-pass method:

```bash
# Basic usage
python -m ocrpolish.cli metadata input/ output/ -h topics/NATO_themes.yaml --flat-topics
```

## Verification

1. Check the output markdown files in the `output/` directory.
2. Verify the `## Categories/Topics` section contains hierarchical tags like `#Category/Topic`.
3. Compare the reasons given with the document text to ensure positive/negative samples were respected.
