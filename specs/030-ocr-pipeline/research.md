# Research & Technical Decisions: OCR Pipeline Integration

## Technical Context Unknowns Resolved

All primary decisions were well-established by the preceding `ocr_multipage_tiff_ollama.py` proof of concept.

### Page Context Injection for Resumes
- **Decision**: When resuming an interrupted OCR job and a page is missing, the system will parse the markdown output to find the exact text of the previous page (if any) and inject it into the prompt.
- **Rationale**: The VLM needs context from the previous page to correctly continue sentences and maintain formatting consistency.
- **Alternatives considered**: Passing the raw image of the previous page (rejected as it doubles API payload size and VLM context length, risking OOM and increasing latency).

### Markdown Parsing for State Validation
- **Decision**: Use a simple Regex-based state parser that looks for the `---\n\n# Page N\n\n` markers to extract page blocks.
- **Rationale**: The output format is rigidly defined by the tool itself. Regex splitting is highly efficient and sufficient for this specific marker structure without needing a full Abstract Syntax Tree (AST) markdown parser.
- **Alternatives considered**: `markdown-it-py` or `mistletoe` (rejected as overly complex for finding sequential page headers).

### Error Recovery & Timeout Handling
- **Decision**: Wrap the Ollama client calls with retries and exponential backoff (already partially present in the PoC script).
- **Rationale**: VLM inference can be slow or temporarily timeout. Graceful degradation prevents crashing a 100-document batch job due to a transient API blip.
