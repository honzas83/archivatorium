# Contract: Native Ollama Compatibility

## Release gate

An unchanged Ollama CLI invocation must remain an unchanged model interaction. This contract is an
absolute release gate and takes precedence over code simplification.

Compatibility is verified in two ways:

1. Complete native request equality plus byte-identical generated files using deterministic mocked
   model responses.
2. No feature-introduced prompt, option, context, retry, timeout, response-processing, or persistence
   change in optional live runs; ordinary model nondeterminism is allowed.

## Metadata and tagging invariants

- Omitted provider is Ollama.
- Metadata CLI model default remains `gemma4:31b`; the compatibility facade's internal default
  remains `gemma4:26b`.
- An omitted metadata host is passed as `None` to the Ollama client so SDK environment resolution
  remains unchanged.
- Structured client timeout remains 300 seconds.
- System instruction and user prompt bytes remain unchanged.
- The schema is appended using the current text and indented JSON serialization.
- Native `format` receives the schema mapping and `options` remains `{"temperature": 0}`.
- `False` remains a boolean; named reasoning remains a string.
- Response extraction, stripping, conditional code-fence cleanup, and Pydantic validation are
  unchanged.
- `retries=3` continues to mean four total validation attempts.
- Only validation errors are retried. Corrective prompt text accumulates exactly as today.
- Primary metadata, conditional final-date, and tagging calls retain their order, schema, model,
  reasoning, windowing, and quality behavior.

## OCR connection invariants

- Host resolution remains explicit truthy `--host`, then `OLLAMA_HOST`, then
  `http://localhost:11434`.
- User and password each retain independent CLI-over-environment precedence.
- DigestAuth is constructed only when both resolved user and password are truthy; partial
  credentials continue to produce an unauthenticated client.
- OCR client timeout remains 240 seconds.
- Omitted model remains `qwen3.5:9b`, mode remains `standard`, reasoning remains `medium`, and DPI
  remains 300.

## OCR request invariants

Every request retains:

```text
model=<selected model>
messages=<current ordered profile messages and image path list>
options={"num_ctx": <current value>, ...profile defaults, ...explicit overrides}
stream=False
think=<present or omitted according to the current profile>
```

- Direct page calls default to `num_ctx=8192`; PDF processing uses `24576`.
- Standard uses its current system/user prompts, prior-page context, no reasoning field, and
  `num_predict=16384`.
- Qwen 3.8 uses its current prompts, prior-page context, command reasoning, and
  `num_predict=16384`.
- GLM has no system message or prior-page context, forces boolean false, and retains temperature,
  top-p, top-k, repetition, and 8192 output defaults.
- FireRed has no system message or prior-page context, omits reasoning, and retains
  `num_predict=16384`.
- Explicit overrides replace only their corresponding default and preserve valid zero/-1 sentinels.

## OCR retry and response invariants

- Messages and kwargs are built once, then reused unchanged.
- Three total attempts are allowed by default.
- Any exception is retried with current exponential delays of two and four seconds.
- Empty visible content remains accepted for Ollama compatibility.
- Dictionary and object response shapes remain accepted; only `message.content` is used.
- Text through the final lowercase `</think>` marker is removed defensively.
- Common ASCII-space indentation is removed only under current rules; relative indentation, tabs,
  blank lines, and remaining whitespace behavior are preserved.

## Traversal, recovery, and output invariants

- Recursively discover and sort PDFs and metadata inputs as today.
- Reuse one command client/engine.
- Preserve relative paths, page headers, page order, and merged separators.
- Completed non-empty pages remain skipped without rendering or inference.
- No-page-header mode continues to disable page-level resume.
- Standard/Qwen previous-page context and GLM/FireRed isolation remain unchanged.
- Temporary PNG deletion remains guaranteed.
- Failed pages/documents do not commit partial replacements.
- Per-file failure continuation, timing counters, output normalization, metadata reconciliation,
  canonical tagging, and archive layout remain unchanged.

## Test rule

Compatibility tests must capture the pre-refactor behavior before the shared client is introduced.
Existing assertions may be strengthened but not weakened, deleted, or rewritten merely to fit the
new abstraction. A failed equality test requires restoring the baseline unless the specification is
explicitly amended by the user.

