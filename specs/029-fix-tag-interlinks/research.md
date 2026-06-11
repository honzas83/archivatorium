# Research: Fix Tag and Interlink Bugs

## Decision: Normalize Slash-Containing Organization and State Names Before Shape Validation

**Rationale**: The current parser splits tags on `/` before validating entity shape. For organization and state tags, that makes legitimate slash-containing names look like malformed hierarchical tags. Normalizing only the entity name portion into a dash-separated value preserves the user's requested metadata while keeping the existing `#Entities/Org/<Name>` and `#Entities/State/<Name>` shape.

**Alternatives considered**:

- Allow hierarchical organization and state tags. Rejected because the specification requires replacing slashes with dashes and preserving the existing fixed-shape tag contract.
- Reject these generated tags and keep warnings. Rejected because this is the bug being fixed and causes metadata loss.
- Apply slash-to-dash normalization to all tag types. Rejected because topics, conceptual tags, and city tags intentionally use hierarchical paths.

## Decision: Preserve Existing Validation for Other Malformed Generated Tags

**Rationale**: The requested bug fix is specific to generated organization and state entity names containing slashes. Existing warnings still provide value for unsupported entity types, empty components, missing names, and invalid city shapes.

**Alternatives considered**:

- Suppress warnings broadly for generated tags. Rejected because it would hide real metadata quality issues.
- Accept any extra organization/state path components without normalization. Rejected because that would change the canonical tag model and indexing behavior.

## Decision: Use Filename-Only Targets for Generated Document Interlinks

**Rationale**: Generated references, body links, and language-version links all point from one generated vault document to another. Filename-only targets are shorter and portable when the target filename is sufficient in the current note context. The change should use the basename of the stored target path when emitting generated document-to-document Markdown links.

**Alternatives considered**:

- Store only filenames in the interlink map. Rejected because internal self-link checks and discovery still benefit from vault-relative paths.
- Shorten every Markdown link in notes. Rejected because unrelated pre-existing links outside generated document interlinking should remain unchanged.
- Compute relative paths from the current file. Rejected because the requested output is the bare target filename, not a relative path.

## Decision: Validate Through Existing Unit and CLI Integration Tests

**Rationale**: The affected behaviors already have adjacent unit tests in `tests/unit/test_tag_parser.py`, `tests/unit/test_interlinking_service.py`, `tests/unit/test_processor_counters.py`, and `tests/unit/test_tagging_service.py`, with CLI/integration coverage in `tests/integration/test_interlink_cli.py` and `tests/integration/test_tagging_pass.py`. Extending these tests gives direct regression coverage without adding new test infrastructure.

**Alternatives considered**:

- Add high-level end-to-end fixture data. Rejected for this narrow bug fix because temporary test vaults and parser text fixtures are sufficient.
- Test only through the CLI. Rejected because parser-level warnings and normalization are easier to isolate at unit level.

## Decision: Remove Hard Maximums From Topic Assignments

**Rationale**: The clarified requirement is to allow every clearly justified taxonomy topic to be assigned. Existing model descriptions and prompt text currently mention a maximum of 10 topics; those instructions can cause under-tagging for dense documents. Topic assignments should remain evidence-based and taxonomy-bound, but should not be discarded solely because a fixed count has been reached.

**Alternatives considered**:

- Raise the cap to a larger fixed number. Rejected because the user explicitly requested an unlimited number of assigned topics.
- Keep the cap and rely on top-100 hints. Rejected because hint breadth does not solve output truncation from an assignment cap.
- Permit arbitrary non-taxonomy topics. Rejected because topic assignments must still come from the approved taxonomy.

## Decision: Use Top 100 Resume-Derived Topic Counter Items as Context

**Rationale**: Resume-derived topic counters help the model stay consistent with prior document processing. Expanding from the current smaller topic hint set to the top 100 improves context coverage while keeping prompt growth bounded and predictable.

**Alternatives considered**:

- Include all topic counter items. Rejected because prompt context would grow without bound.
- Keep the existing smaller topic hint count. Rejected because it does not satisfy the clarified top-100 requirement.
- Merge topic counters with conceptual/entity counters. Rejected because counters serve different canonical tag categories and topic hints must remain subordinate to taxonomy.
