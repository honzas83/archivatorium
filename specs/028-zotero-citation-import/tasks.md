# Implementation Tasks: 028-zotero-citation-import

**Status**: Completed
**Total Tasks**: 4

## Phase 1: Core Implementation

- [x] T001 Implement `format_coins_span` in `ocrpolish/utils/metadata.py` to generate COinS ContextObjects, mapping language and citekey to standard tags.
- [x] T002 Update `generate_citation_callout` in `ocrpolish/utils/metadata.py` to include the invisible COinS span and remove the CSL-JSON block.
- [x] T003 Remove old `--zotero` flag from CLI.
- [x] T004 Run tests and validation.
