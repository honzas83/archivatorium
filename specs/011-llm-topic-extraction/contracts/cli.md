# CLI Contract: Metadata with Topics

## Command: `ocrpolish metadata`

### Updated Arguments & Options
- `INPUT_DIR`: Path to input directory.
- `OUTPUT_DIR`: Path to output directory.
- `--hierarchy-file`, `-h`: (NEW) Path to the YAML topic hierarchy. If provided, enables topic extraction.
- `--model`, `-m`: Ollama model to use.
- ... (existing metadata options)

### Integration Behavior
1. Read file and extract initial frontmatter/body.
2. Call LLM for primary metadata extraction (using existing `MetadataSchema`).
3. If `--hierarchy-file` is set:
    a. Load hierarchy.
    b. Combine extracted Abstract + First Chunk of text.
    c. Step 1: LLM selects categories.
    d. Step 2: LLM selects topics within categories.
    e. Format topics as hierarchical tags (e.g., `#Category/Topic`).
    f. Add these tags to the `tags` list in frontmatter.
    g. Append these tags to the Abstract callout in the document body.
4. Write the final document.
