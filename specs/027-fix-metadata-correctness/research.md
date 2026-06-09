# Research: Metadata Correctness Fixes

## Decision: Share a generated-document eligibility rule across resume and finalization surfaces

**Rationale**: Resume preflight currently scans output Markdown broadly, while interlinking/finalization excludes index pages, hidden/system folders, and templates. A single document eligibility predicate prevents support-file tags from becoming dynamic tagging vocabulary and makes skip handling testable.

**Alternatives considered**:
- Keep separate resume and interlink exclusion lists: rejected because drift caused the current counter contamination risk.
- Filter only by filename suffix: rejected because support files also live in folders and common landing names.

## Decision: Count skipped existing outputs through the scanned-file registry

**Rationale**: The processor already tracks `scanned_files_tags` by path and uses it when updating counters. Skip handling should use the same registry: if preflight scanned a file, it is already counted; if not, parse it once and register it.

**Alternatives considered**:
- Always parse skipped outputs: rejected because preflight-plus-skip would double count.
- Never parse skipped outputs: rejected because files outside preflight would be missing from counters.

## Decision: Pass resume counters to tagging as compact category-specific hints

**Rationale**: Existing counters distinguish conceptual tags, topics, and entities. Tagging should receive conceptual counter paths as preferred `#Tags` vocabulary, entity counters as preferred `#Entities` vocabulary, and topic counters only as subordinate hints under the taxonomy.

**Alternatives considered**:
- Continue passing conceptual tags only through metadata prompt context: rejected because it does not guide the tagging pass directly.
- Merge all counters into one hint list: rejected because it blurs canonical categories and can bias topics/entities incorrectly.

## Decision: Enforce conceptual tag quality in the initial tagging call

**Rationale**: The failure mode is an initial tagging response with topics/entities but no conceptual tags. The prompt, structured schema, and post-parse validation must all express the same requirement: substantive documents need at least five conceptual tags. No separate repair phase is needed because it would hide the quality failure and add another LLM path.

**Alternatives considered**:
- Add a conceptual-tag repair call: rejected by the feature scope and because it would accept incomplete initial tagging.
- Keep optional Pydantic defaults without validation: rejected because omitted fields would silently become empty successes.

## Decision: Detect non-substantive administrative stubs deterministically

**Rationale**: Empty conceptual tags are acceptable only for genuinely administrative stubs. A conservative classifier based on cleaned source text and boilerplate patterns keeps uncertain and content-bearing short documents in the substantive path.

**Alternatives considered**:
- Use short length as the main criterion: rejected because short policy, organizational, procedural, command, exercise, or reference notes can still be substantive.
- Ask the LLM whether the source is substantive: rejected because the acceptance gate must be deterministic before accepting empty conceptual tags.

## Decision: Preserve useful conceptual vocabulary during duplicate suppression

**Rationale**: Conceptual tags often intentionally overlap semantically with topics and entities. Suppression should remove exact duplicates of entity names or topic components, but not erase justified archival concepts, useful acronyms, exercise names, or preferred-vocabulary paths merely because related topics/entities exist. Preservation must be driven by the static useful-tags vocabulary and resumed conceptual counters, not hardcoded domain-term lists.

**Alternatives considered**:
- Keep broad component-based suppression: rejected because it can erase all useful `#Tags`.
- Disable suppression entirely: rejected because exact duplicate entity/topic names still add noise.

## Decision: Remove legacy fallback migration from production indexing/export

**Rationale**: `CanonicalTagParser` already recognizes only `#Entities/...`, `#Topics/...`, and `#Tags/...`. Indexing and XLSX export should use that canonical result directly and should not reinterpret obsolete unprefixed tags into canonical columns.

**Alternatives considered**:
- Keep compatibility fallbacks for old vaults: rejected because the canonical model is now authoritative.
- Migrate obsolete tags during export: rejected because export must not silently create canonical data from legacy formats.

## Decision: Preserve hierarchical conceptual tag paths

**Rationale**: The canonical `#Tags/...` namespace supports useful path-like conceptual tags, including exercise/year forms such as `#Tags/WINTEX/73`. Parser validation, resume counters, duplicate suppression, rendering, indexing, and spreadsheet export must preserve the full path instead of warning that a multi-component conceptual tag is malformed.

**Alternatives considered**:
- Restrict conceptual tags to one path component: rejected because it contradicts the prompt and loses legitimate archival vocabulary.
- Flatten hierarchical tags during parsing: rejected because it changes canonical data and can create ambiguous collisions.

## Decision: Mirror PDFs beside generated Markdown outputs

**Rationale**: Recursive source-tree mirroring needs local PDF folders for each generated Markdown folder. A single output-root `pdf/` directory breaks relative organization for nested collections, while a local `pdf/` directory keeps generated source links stable and inspectable.

**Alternatives considered**:
- Keep all PDFs under one output-root `pdf/`: rejected because nested documents need per-folder PDF organization.
- Store PDFs next to Markdown without a `pdf/` subfolder: rejected because it pollutes document folders and changes existing source-link expectations.

## Decision: Make metadata mask and dry-run safety explicit at orchestration boundaries

**Rationale**: The metadata CLI currently enumerates all files for mirroring and enrichment decisions. Mask must limit enrichment targets, `.filtered.md` sidecars must never be enriched, and dry-run must avoid all writes, copies, hardlinks, vault initialization, sidecars, and output updates.

**Alternatives considered**:
- Let dry-run call lower-level mirror/write helpers conditionally: rejected because the safest user contract is no mutation from the metadata command when dry-run is set.
- Apply mask only to Markdown discovery helper while mirroring all files: accepted only for mirroring when not dry-run; nonmatching Markdown must not be enriched.
