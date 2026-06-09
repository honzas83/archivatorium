# Quickstart: Canonical Tag Data Layer

This guide shows how to run the new canonical tag parser, run indexing, and inspect tag counters and diagnostic warnings.

---

## 1. Running the Tag Parser programmatically

You can parse generated Markdown content directly in Python using the new `CanonicalTagParser` utility:

```python
from pathlib import Path
from ocrpolish.utils.tag_parser import CanonicalTagParser

content = """
# Document Title

This document details the command structures.

> [!abstract]
> ## Categories/Topics
> - #Topics/Force-Planning/Command-Structure — Consultation reasoning
> 
> ## Entities
> * States
>   - #Entities/State/United-States
>   - #Entities/State/France
> * Organisations
>   - #Entities/Org/NATO
> * Cities
>   - #Entities/City/United-Kingdom/London
>   - #Entities/City/Berlin  <-- Invalid (Missing State)
> 
> ## Tags
> #Tags/Strategic-Concept #Tags/Command-Post
"""

parser = CanonicalTagParser()
parsed_tags = parser.parse_text(content, file_path=Path("sample.md"))

# Access clean, normalized paths
print("Conceptual Tags:", parsed_tags.conceptual_tags)
# Output: {'strategic-concept', 'command-post'}

print("States:", parsed_tags.entities["State"])
# Output: {'united-states', 'france'}

print("Orgs:", parsed_tags.entities["Org"])
# Output: {'nato'}

print("Cities:", parsed_tags.entities["City"])
# Output: {'united-kingdom/london'}
# Note: 'Berlin' is omitted and logs a warning!

print("Topics:", parsed_tags.topics)
# Output: {'force-planning/command-structure'}
```

---

## 2. Running the CLI commands

The `metadata` and `index` commands automatically leverage the new canonical tag layer.

### 2.1. Extract metadata and tags

Run the metadata extractor on a source directory. The tagging service will generate canonical tags into the body callout block:

```bash
ocrpolish metadata data/source data/output \
  --hierarchy-file topics/taxonomy.yaml \
  --tags-file topics/vocabulary.yaml
```

### 2.2. Generate index and reports

Run the index builder to generate Obsidian index pages (e.g. `Index - States.md`, `Index - Cities.md`) and the XLSX report, powered by the canonical structured tags:

```bash
ocrpolish index data/output data/output
```

---

## 3. Viewing Warnings & Diagnostics

If a malformed tag is encountered (e.g. `#Entities/City/London` lacking state, or `#Entities/Country/France` containing an unsupported type), the processor ignores the tag and outputs a warning to the standard log:

```text
[WARNING] Malformed generated tag ignored: #Entities/City/London (City tag must have format #Entities/City/<State>/<City>)
[WARNING] Malformed generated tag ignored: #Entities/Country/France (Unsupported entity type: Country)
```
These warnings will help keep the vault's taxonomy clean and warn if the LLM output is drifting from the taxonomy rules.
