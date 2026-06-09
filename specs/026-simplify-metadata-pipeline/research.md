# Research: Simplify Metadata Pipeline

## Decision: Default vault and PDF roots to the output directory, but link only to mirrored vault PDFs

**Rationale**: The production command needs backward-compatible defaults while generated Markdown must be portable inside the generated Obsidian vault. Treating the output directory as the effective vault root and PDF root keeps existing command ergonomics, while deriving `source` from the mirrored `pdf/` layout prevents links from exposing or depending on the input lookup directory.

**Alternatives considered**:
- Keep `vault_root` and `pdf_dir` unset internally: rejected because link generation currently has multiple fallback behaviours and can drift from the required `[[pdf/<filename>.pdf]]` contract.
- Generate source links from the source PDF lookup path: rejected because it breaks vault portability and conflicts with the spec.

## Decision: Make flat tagging the only production topic extraction mode

**Rationale**: The current production metadata path already uses `TaggingService` for generated topics/entities/tags. Keeping `TopicExtractor` and two-step topic extraction in the runtime package leaves obsolete behaviour available and makes tests ambiguous. Removing the runtime dependency and production tests for non-flat extraction aligns production behaviour with the flat tagging service path.

**Alternatives considered**:
- Keep a deprecated `--flat-topics` switch with flat as default: rejected because a non-flat switch would still expose a production mode.
- Keep legacy tests as skipped production tests: rejected because skipped tests still document obsolete production behaviour.
- Retain old evaluation logic outside `ocrpolish/`: accepted only if clearly outside the package runtime path.

## Decision: Refactor file processing into explicit stage methods with result records

**Rationale**: `MetadataProcessor.process_file` currently combines reading, generated-section stripping, prompt creation, extraction, reconciliation, rendering, writing, and counter ingestion. Stage methods with explicit input/output records allow focused tests for compatibility-critical behaviour without forcing every regression test through LLM mocking and filesystem writes.

**Alternatives considered**:
- Keep one method and add more integration tests: rejected because failures remain hard to isolate and the method remains difficult to maintain.
- Introduce a separate pipeline framework: rejected as unnecessary for a single CLI package and likely to increase complexity.

## Decision: Precompute static taxonomy and useful-tag prompt text during tagging service initialization

**Rationale**: Sliding-window tagging currently calls prompt generation per chunk. When static taxonomy YAML and useful-tag text are rebuilt each time, large documents pay repeated serialization and flattening costs. Computing normalized themes, flattened taxonomy, dumped taxonomy text, and useful-tag prompt text once per service instance preserves output semantics while reducing per-window overhead.

**Alternatives considered**:
- Cache only the YAML dump lazily on first prompt: rejected because initialization-time precomputation is simpler to test and matches the requirement.
- Recompute per chunk for freshness: rejected because taxonomy and useful-tag files are fixed for the service lifetime.

## Decision: Use existing helpers for compatibility-critical rendering and ingestion

**Rationale**: Existing helpers already encode frontmatter rendering, metadata table formatting, citation generation, generated section stripping, citekey generation, reconciliation, mirroring, and canonical tag parsing. The refactor should reorganize the pipeline while preserving these helpers where their behaviour is already tested and compatible.

**Alternatives considered**:
- Rewrite rendering and parsing as part of the pipeline refactor: rejected because it increases compatibility risk without being required by the feature.
