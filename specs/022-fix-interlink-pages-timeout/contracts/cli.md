# CLI Contract: fix-interlink-pages-timeout

The changes in this feature do not introduce new CLI commands but modify the behavior of existing ones.

## `ocrpolish metadata`
- Now calculates the page count correctly even if page numbers are non-sequential.
- Respects the new global Ollama timeout.

## `ocrpolish interlink`
- Correctly links documents that use different naming conventions for the same organizational group (e.g., Staff Group vs SG).
- **New Option**: `--unifications <path>` allows specifying a custom YAML file for normalization rules.
