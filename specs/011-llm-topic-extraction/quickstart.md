# Quickstart: Integrated Topic Extraction

## Installation
Ensure `ollama` is running and the required model is pulled:
```bash
ollama pull gemma4:26b
```

## Basic Metadata Extraction (No Topics)
```bash
python -m ocrpolish metadata data/input data/output
```

## Metadata Extraction with Topics
To enable topic extraction, provide the `--hierarchy-file` (or `-h`) flag:
```bash
python -m ocrpolish metadata data/input data/output --hierarchy-file topics/NATO_themes.yaml
```

## Verification
Open a processed markdown file in Obsidian. 

1. **Frontmatter**: You should see hierarchical tags in the `tags` list.
2. **Abstract**: You should see the same tags at the bottom of the `[!abstract]` callout.

Example:
```markdown
---
tags:
  - Doctrine-and-Strategy/Nuclear-Deterrence
---
> [!abstract] Abstract
> This document discusses...
>
> #Doctrine-and-Strategy/Nuclear-Deterrence
```
