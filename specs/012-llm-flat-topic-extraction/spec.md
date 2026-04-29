# Feature Specification: LLM Flat Topic Extraction

**Feature Branch**: `012-llm-flat-topic-extraction`  
**Created**: 2026-04-29  
**Status**: Draft  
**Input**: User description: "In this specification, we will try to use single-step, flat topics with the whole Category/Topic hierarchy passed to LLM, because if the model selects categories, it does not have an access to positive / negative samples."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Single-step classification (Priority: P1)

As a system processing OCR text, I want to identify the most relevant topics from a flat hierarchy in a single LLM call, so that the model can use positive and negative samples to make more accurate decisions.

**Why this priority**: This is the core functional change requested to improve topic extraction accuracy.

**Independent Test**: Can be tested by providing a document and a flattened hierarchy with samples, then verifying the LLM returns appropriate topics.

**Acceptance Scenarios**:

1. **Given** a text document and a configuration containing categories and topics with samples, **When** the system constructs a flat list of topics including their samples, **Then** the LLM identifies the correct topics in one pass.
2. **Given** a hierarchy where some topics have negative samples, **When** the classification runs, **Then** the LLM avoids selecting topics where the text matches negative samples.

---

### User Story 2 - Hierarchy Flattening (Priority: P2)

As a system, I want to automatically transform the nested Category/Topic structure into a flat list format suitable for LLM prompts, so that I don't have to manually prepare the prompt context.

**Why this priority**: Essential for supporting the single-step classification workflow without manual intervention.

**Independent Test**: Can be tested by providing a nested YAML/JSON hierarchy and verifying the output is a correctly formatted flat list.

**Acceptance Scenarios**:

1. **Given** a multi-level category/topic hierarchy, **When** the flattening service is called, **Then** it produces a flat list where each item contains the full path (Category > Topic) and associated samples.

---

### User Story 3 - Accuracy Comparison (Priority: P3)

As a developer, I want to compare the results of the flat classification with the previous multi-step approach, so that I can quantify the accuracy improvement.

**Why this priority**: Validates the hypothesis that flat classification is better for this use case.

**Independent Test**: Run both methods on a set of gold-standard documents and compare F1 scores.

**Acceptance Scenarios**:

1. **Given** a set of documents with known correct topics, **When** processed with both flat and multi-step methods, **Then** the flat method shows higher precision and recall for topics with complex sample sets.

---

### Edge Cases

- **Hierarchy too large**: What happens when the flattened hierarchy with all samples exceeds the LLM's context window?
- **Ambiguous samples**: How does the system handle cases where positive samples for one topic overlap significantly with another?
- **No samples**: How does the system handle topics or categories that lack positive/negative samples?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST be able to load a nested hierarchy of Categories and Topics from configuration.
- **FR-002**: System MUST include both positive and negative samples for each topic in the LLM prompt.
- **FR-003**: System MUST provide the entire flat hierarchy in a single LLM request.
- **FR-004**: System MUST format the flat hierarchy as YAML to ensure the LLM understands the relationships while maintaining token efficiency.
- **FR-005**: System MUST map the LLM's selected flat topics back to the original Category/Topic structure for reporting.

### Key Entities *(include if feature involves data)*

- **Topic**: A specific thematic label with positive and negative text samples.
- **Category**: A group of related topics, used for organization but potentially omitted as a separate selection step in this feature.
- **FlatHierarchy**: A linearized representation of all Categories and Topics designed for LLM consumption.

### Assumptions

- **A-001**: The source configuration already contains positive and negative samples for the majority of topics.
- **A-002**: The LLM context window is large enough (at least 8k-16k tokens) to accommodate the full flat hierarchy for typical datasets.
- **A-003**: The mapping from flat topics back to categories is deterministic based on the hierarchy structure.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Topic extraction accuracy (F1 score) increases by at least 15% compared to the two-step (Category -> Topic) selection method.
- **SC-002**: System can process hierarchies with up to 100 topics and their samples in a single pass without exceeding 8k tokens.
- **SC-003**: 100% of selected topics are correctly mapped back to their parent categories in the final output.
- **SC-004**: LLM response parsing failure rate is below 1%.
