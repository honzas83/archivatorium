# Research: Unified LLM Providers

## Decision: Use one application-facing client with two transports

**Decision**: Metadata, tagging, and OCR depend on one shared LLM client. The client delegates wire
translation to a native Ollama transport or an OpenAI-compatible e-INFRA transport.

**Rationale**: This removes the current split between the structured Ollama wrapper and direct OCR
SDK use while keeping provider differences out of archival workflows. It permits exact Ollama
requests and correct e-INFRA requests without reducing both providers to a lowest common denominator.

**Alternatives considered**:

- Add a second e-INFRA wrapper beside the current paths: rejected because OCR and structured calls
  would remain duplicated and consumers would branch on provider.
- Use one broad multi-provider framework: rejected because only two providers are in scope and an
  additional translation layer makes Ollama parity harder to prove.

## Decision: Preserve Ollama through its native API

**Decision**: Keep `ollama.Client.chat()` as the Ollama transport. Reproduce current kwargs,
prompts, images, schema format, reasoning types, option names, timeouts, response handling, and retry
semantics exactly.

**Rationale**: The application relies on native fields including `images`, `format`, `think`,
`num_ctx`, `num_predict`, top-k, and repetition controls. Metadata and OCR also use different
established timeouts and retry meanings. The compatibility requirement prohibits changing these
semantics merely to share a protocol.

**Alternatives considered**:

- Route Ollama through its OpenAI-compatible endpoint: rejected because Ollama documents partial
  compatibility and the current native option surface is wider. See
  <https://docs.ollama.com/api/openai-compatibility>.
- Normalize both Ollama retry loops immediately: rejected because structured extraction currently
  permits four total attempts while OCR permits three and retries different error classes.

## Decision: Parallelize independent PDFs, not dependent pages

**Decision**: Add bounded OCR concurrency across PDF files. Keep every page chain within one PDF
sequential and retain one output/resume boundary per document. Expose `--concurrency`, defaulting to
one and capping the value at four.

**Rationale**: Standard and Qwen 3.8 modes use the preceding page transcription as model context.
Parallelizing pages would silently remove or weaken that input. Independent PDFs have no such data
dependency, so they can overlap safely while preserving page order, retries, and recovery.

**Alternatives considered**:

- Parallelize pages within one PDF: rejected because adjacent-page context would be unavailable for
  simultaneous requests and completed pages could not be persisted through the existing ordered
  resume path without changed semantics.
- Create a separate client for each worker: rejected for e-INFRA because one command-scoped client
  can share connection resources and a thread-safe capability cache.

## Decision: Use the official OpenAI client for e-INFRA Chat Completions

**Decision**: Add the official OpenAI Python client and configure it with
`https://llm.ai.e-infra.cz/v1` and Bearer authentication. Use Chat Completions rather than assuming
other OpenAI endpoints are supported.

**Rationale**: e-INFRA describes the endpoint as OpenAI-compatible, notes that not every endpoint is
supported, and recommends the OpenAI or LiteLLM clients. The official client supplies custom base
URLs, typed errors, JSON Schema requests, multimodal content, and streaming without a broad
multi-provider dependency. See <https://docs.cerit.io/en/docs/ai-as-a-service/ai-api>.

**Alternatives considered**:

- Use raw httpx: rejected because it would require custom streaming and error-protocol handling.
- Use LiteLLM: rejected because its provider breadth is unnecessary and adds another translation
  layer between compatibility tests and the endpoint.

## Decision: Start with exact model `qwen3.8-27b`

**Decision**: When e-INFRA is selected and the model is omitted, use `qwen3.8-27b` for metadata and
OCR. Allow an explicit model override and report unavailability without automatic substitution.

**Rationale**: e-INFRA currently lists the model with chat and multimodal capabilities, a 256K
context window, 32K maximum output, and configurable thinking. Exact names may be retired, but the
stable `coder` and `agentic` aliases select the different Flash model. See
<https://docs.cerit.io/en/docs/ai-as-a-service/chat-ai>.

**Alternatives considered**:

- Use `coder` or `agentic`: rejected because neither selects the requested 27B model.
- Make Qwen 3.8 the global default: rejected because it would break both Ollama command defaults.

## Decision: Add provider configuration without replacing existing options

**Decision**: Add `--llm-provider`, `--llm-base-url`, and `--llm-api-key-file` to both model
commands. Keep `--host` as an endpoint alias. Resolve omitted model defaults only after the provider
is known, using explicit-option awareness so an explicitly selected model always wins.

**Rationale**: Existing commands remain valid while new commands use the same concepts. Resolution
before filesystem or network work gives configuration failures predictable, side-effect-free
behavior.

**Alternatives considered**:

- Infer provider from URL: rejected because custom Ollama and compatible endpoints are ambiguous.
- Reuse `--user` and `--password` for Bearer authentication: rejected because it changes their
  existing DigestAuth meaning.

## Decision: Use explicit secure e-INFRA credential sources

**Decision**: Resolve e-INFRA credentials from an explicitly selected key file first, then
`E_INFRA_API_TOKEN`. Do not consume `OPENAI_API_KEY` and do not auto-read `meta-api-key`. Trim
surrounding whitespace, reject empty/unreadable/insecure files, redact secret-bearing values, and
add `/meta-api-key` to `.gitignore`.

**Rationale**: Explicit sources avoid accidentally sending archival content with an unrelated
credential. The current local file is untracked but not ignored and is group/world-readable, so it
must be protected before live validation.

**Alternatives considered**:

- Accept a literal token option: rejected because command histories and process listings may expose
  it.
- Auto-discover the repository file: rejected because credentials must not become repository
  convention or activate remote processing implicitly.

## Decision: Translate reasoning at the provider boundary

**Decision**: Retain the public `False|low|medium|high` type. Send the current boolean/string value
to Ollama. Send `none|low|medium|high` as `reasoning_effort` to e-INFRA.

**Rationale**: Minimal live probes established that `reasoning_effort=none` disables Qwen 3.8
reasoning and `low` yields valid visible structured output. Generic chat-template flags did not
disable reasoning in this deployment. Translation belongs inside the provider transport and must
not change OCR-profile precedence.

**Alternatives considered**:

- Forward Ollama's boolean false to e-INFRA: rejected because it is not the observed compatible
  representation.
- Expose different reasoning options per provider: rejected because the existing CLI contract is
  sufficient and consistent.

## Decision: Share structured validation without changing Ollama prompt bytes

**Decision**: The shared client owns the fixed structured system instruction, schema text appended
to the user prompt, code-fence cleanup, Pydantic validation, and corrective validation retry. The
Ollama transport sends the native schema format; e-INFRA sends OpenAI JSON Schema response format.

**Rationale**: Both workflows require the same validated model objects. A live e-INFRA probe with
`qwen3.8-27b` accepted JSON Schema and returned valid JSON. Keeping schema text in the prompt
preserves Ollama behavior and supplies an explicit instruction for both providers.

**Alternatives considered**:

- Use SDK-specific automatic parsing: rejected because shared manual validation provides identical
  cleanup and validation behavior.
- Remove the schema from the prompt: rejected because it would change existing Ollama model input.

## Decision: Translate images only inside transports

**Decision**: A shared message carries text plus local image attachments. Ollama receives the
current image-path list. e-INFRA receives base64 data URLs in OpenAI image content parts.

**Rationale**: The OCR engine should not know SDK formats. Qwen 3.8 is advertised as multimodal, and
both provider contracts accept image input in different shapes.

**Alternatives considered**:

- Upload images to a public URL: rejected for privacy, lifecycle, and availability reasons.
- Put base64 encoding in the OCR engine: rejected because it leaks provider protocol into workflow
  logic.

## Decision: Stream e-INFRA OCR and return one visible response

**Decision**: Use streaming for e-INFRA OCR, consume chunks inside the transport, discard separate
reasoning content, and return one assembled visible response. Do not change Ollama's non-streaming
request.

**Rationale**: e-INFRA documents a fixed non-streaming infrastructure timeout and recommends
streaming for long calls. OCR can produce long page responses. The transport can hide incremental
delivery and prevent partial pages from being committed. See
<https://docs.cerit.io/en/docs/ai-as-a-service/ai-api>.

**Alternatives considered**:

- Use non-streaming everywhere: rejected because long remote OCR may fail regardless of the client
  timeout.
- Stream Ollama too: rejected because it changes the established request and response path.

## Decision: Make output exhaustion explicit

**Decision**: Use initial e-INFRA allowances of 8,192 tokens for structured calls and 16,384 for
OCR. Treat a length finish, exhausted reasoning-only response, or missing visible content as a
distinct failure instead of a valid empty result.

**Rationale**: Live probing showed a small completion budget can be consumed entirely by reasoning.
The chosen starting values fit within the model's documented 32K maximum. Ollama structured calls
must not receive a new output limit.

**Alternatives considered**:

- Rely on service defaults: rejected because reasoning makes visible-output capacity unpredictable.
- Apply these limits to Ollama: rejected because that would alter existing inference semantics.

## Decision: Reject unsupported combinations before processing

**Decision**: e-INFRA supports temperature, top-p, positive output limits, and shared reasoning.
Reject explicit top-k, repetition settings, unlimited output, e-INFRA credentials with Ollama,
DigestAuth settings with e-INFRA, and the e-INFRA/GLM OCR combination. Do not silently drop settings.

**Rationale**: GLM mode's established meaning includes native sampling and repetition defaults.
Silent omission would violate explicit user intent and mode compatibility. Provider and mode remain
independent because the system reports incompatibility rather than replacing either choice.

**Alternatives considered**:

- Forward undocumented fields: rejected because acceptance does not prove inference effect.
- Ignore unsupported fields: rejected because the result would not represent the selected command.

## Decision: Normalize remote errors but freeze Ollama retry behavior

**Decision**: Categorize remote configuration, authentication, invalid request, unknown model,
unsupported capability, rate limit, transient service, truncation, empty response, interrupted
stream, and validation failures. Retry only safe transient/validation cases with bounded backoff and
`Retry-After`; disable hidden SDK retries. Preserve existing Ollama retry loops and log outcomes.

**Rationale**: One error vocabulary prevents workflows from parsing provider exceptions. Avoiding
double retries makes call counts deterministic, while retaining Ollama policy satisfies the
compatibility gate.

**Alternatives considered**:

- Let each SDK retry implicitly: rejected because call counts, delays, and terminal behavior become
  opaque.
- Apply the new retry matrix to Ollama: rejected because it changes established failure semantics.

## Decision: Prove compatibility before and after migration

**Decision**: First add characterization tests for complete Ollama requests and deterministic output
bytes. Then add shared contract tests, provider translation tests, CLI integration tests, and
doubly-opt-in live e-INFRA smoke tests using only synthetic data.

**Rationale**: Current tests cover many individual fields but not the full compatibility surface.
Capturing the baseline before refactoring prevents updated mocks from blessing a behavior change.
The e-INFRA service prohibits uncoordinated benchmarking, so live validation is minimal, sequential,
and functional rather than comparative.

**Alternatives considered**:

- Rely only on existing tests: rejected because host/auth precedence, cumulative structured retries,
  complete request equality, and byte-level outputs are not fully characterized.
- Put live calls in normal pytest: rejected because credentials, service availability, and
  sensitive-data controls make them unsuitable as default tests.
