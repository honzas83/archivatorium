# Research: Precision Tagging System

## Decision 1: Dynamic Pass vs. Static Sliding Window
- **Decision**: Implement a **Dynamic Tagging Pass**. Use a single pass for documents within the model's context window (e.g., 32,768 tokens for `gemma4:31b`) and fallback to a manual sliding window for larger files.
- **Rationale**: 
    - Single-pass processing is faster and avoids the complexity of merging/deduplicating tags across chunks for most documents.
    - Large models like `gemma4:31b` provide sufficient context to handle many archival documents in one go.
    - Retaining the manual sliding window ensures that extremely large documents are still processed comprehensively without silent truncation or memory exhaustion.
- **Alternatives Considered**: 
    - **Always Sliding Window**: Rejected as inefficient for documents that fit in context.
    - **Pure Single Pass with Truncation**: Rejected because archival integrity requires processing the full document.

## Decision 2: Token Count Estimation
- **Decision**: Use a lightweight tokenizer (e.g., `tiktoken` or a simple word-count heuristic with a safety buffer) to estimate token count before the tagging pass.
- **Rationale**: 
    - To decide between Single Pass and Sliding Window, the system needs a reliable estimate of the token count.
    - Heuristics (e.g., 0.75 words per token) are often sufficient when combined with a conservative buffer (e.g., aiming for 28k tokens if the limit is 32k).

## Decision 3: Model Configuration (`think: false`)
- **Decision**: Use `ollama.chat(..., think=False)` for the Step 2 tagging pass.
- **Rationale**: 
    - Disabling "thinking" (reasoning) mode reduces latency significantly for models like DeepSeek-R1 and Gemma-based reasoning models.
    - For high-volume tagging, raw extraction precision is prioritized over long-form chain-of-thought reasoning.

## Decision 4: Tag Aggregation and Deduplication
- **Decision**: Use a frequency-weighted set union for aggregation (in sliding window mode), followed by strict suppression.
- **Rationale**:
    - **Entities & Topics**: Set union is sufficient.
    - **Conceptual Tags**: Frequency tracking identifies globally relevant tags across multiple windows.
    - **Suppression**: Applying strict suppression after aggregation ensures that if a concept is captured as a topic or entity anywhere in the document, it is removed from the flat tags globally.

## Decision 5: Performance Targets
- **Decision**: Target ~30-60 seconds for a single 32k context prefill/extraction on high-end GPUs.
- **Rationale**: Large context processing requires substantial compute. For multi-chunk documents, sliding window latency scales linearly with the number of chunks.
