# Research: fix-interlink-pages-timeout

## Archive Code Unification (Modular Design)

### Rule Storage & format
The unification rules will be stored in `topics/unifications.yaml`. This allows the user to add new rules without modifying the codebase.
The YAML format will be a list of mapping objects:
```yaml
unifications:
  - pattern: "\\(Staff[ -]?Group\\)"
    replacement: "(SG)"
  - pattern: "\\(Study[ -]?Group\\)|Study/"
    replacement: "(STUDY)"
```

### Regex Implementation
Python's `re.sub` with `flags=re.IGNORECASE` will be used to apply these rules.
Since rules are applied **globally**, we must be careful with overlapping patterns. Longest patterns or specific ordering in the YAML file will be respected.

## Page Counting
The header-count method is confirmed as the most robust way to handle non-sequential OCR page numbers.
```python
def extract_page_count_from_headers(content: str) -> int:
    # Count occurrences of "# Page [Number]" at start of line
    return len(re.findall(r"^# Page \d+", content, re.MULTILINE))
```

## Ollama Timeout
Setting `timeout=300.0` in the `ollama.Client` constructor is the correct approach to prevent indefinite hangs.
