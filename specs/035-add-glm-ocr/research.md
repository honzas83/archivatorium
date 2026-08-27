# Phase 0 Research: Add GLM OCR Mode

## Decision 1: Treat the remote Ollama API as the inference contract

**Decision**: Continue using the existing official Ollama client as transport, but design and test the request against `POST /api/chat`: `model`, `messages`, `stream`, and top-level `think` are request fields, while sampling and generation controls belong in `options`. Do not base the feature on the locally installed client version and do not add a client-version pin solely for this mode. Document Ollama server 0.9.0 or newer as a GLM-mode prerequisite because that release added API thinking control.

**Rationale**: The application already connects to configurable local or remote Ollama hosts. The [official chat API contract](https://docs.ollama.com/api/chat) defines `think` independently from `options`, and Ollama states that the same API is available for local and cloud hosts in its [API introduction](https://docs.ollama.com/api/introduction). Ollama's [0.9.0 release notes](https://github.com/ollama/ollama/releases/tag/v0.9.0) identify that release as the introduction of API thinking enable/disable behavior. This keeps the server API—not one workstation's package state—as the source of truth.

**Alternatives considered**:

- Call a new raw HTTP implementation: rejected because the current official client already transports the same API request and preserves authentication/timeout behavior.
- Switch to `/api/generate`: rejected because the existing multimodal flow uses chat messages and the chat endpoint directly supports images, runtime options, and thinking control.
- Pin to the locally observed client version: rejected because deployment targets remote API hosts and the local environment is not the compatibility boundary.

## Decision 2: Name the existing mode `standard`

**Decision**: Add `--mode` as a `standard|glm` CLI choice with `standard` as the default. Omission and explicit `standard` both select the unchanged existing VLM behavior. Internally, resolve both values to immutable mode profiles that do not contain a model name.

**Rationale**: The existing behavior is the standard OCR mode, not a deprecated or transitional legacy path. Naming it explicitly makes help and configuration clear while omission remains backward compatible and `--model` remains structurally independent.

**Alternatives considered**:

- Call the existing mode `legacy` or `generic`: rejected because the authoritative product terminology is `standard`.
- Add a separate `glm-ocr` command: rejected because rendering, traversal, retry, resume, and output behavior are shared.
- Create a GLM-specific engine subclass: rejected because only request construction and mode defaults differ.

## Decision 3: Build a native, isolated GLM page request

**Decision**: For each GLM page, send one user message containing the page image and the exact content `Text Recognition:`. Do not send the generic system prompt. Send `think: false` as a top-level chat field and never append previous-page OCR text. Enforce page isolation both in the run loop and in the request builder so direct calls, resume, missing-page recovery, and retries cannot leak context.

**Rationale**: The official [GLM-OCR model page](https://ollama.com/library/glm-ocr) documents `Text Recognition:` for text extraction. The [thinking capability documentation](https://docs.ollama.com/capabilities/thinking) places thinking control on the chat/generate request. Defense-in-depth ensures the independence guarantee applies to every path, not only normal sequential processing.

**Alternatives considered**:

- Keep the generic system message and replace only the user prompt: rejected because the resulting request would no longer be the native minimal GLM-OCR prompt.
- Suppress previous-page context only in `run_ocr`: rejected because direct or future callers could still pass context into a GLM request.
- Hide reasoning text only in the saved output: rejected because the requirement is to disable reasoning at inference time.

## Decision 4: Resolve inference options by profile, then explicit CLI override

**Decision**: Define the GLM profile defaults as `temperature=0.0`, `top_p=0.00001`, `top_k=1`, `repeat_penalty=1.1`, and `num_predict=8192`. Each new CLI option defaults to `None`; only non-`None` values replace profile defaults. Preserve the current `num_ctx` behavior because it is outside the requested default set. In standard mode with no overrides, send exactly the existing options; explicit overrides may tune the same named API options without changing prompts or context behavior.

**Rationale**: `None` distinguishes omission from an intentional zero. The official [GLM-OCR configuration](https://github.com/zai-org/GLM-OCR/blob/main/glmocr/config.yaml) defines the requested prompt and values as `max_tokens`, `temperature`, `top_p`, `top_k`, and `repetition_penalty`. The native Ollama [Modelfile parameter reference](https://docs.ollama.com/modelfile) confirms the corresponding API option names `num_predict`, `temperature`, `top_p`, `top_k`, and `repeat_penalty`. A profile-first merge keeps mode responsible for defaults while preserving explicit user control.

**Alternatives considered**:

- Put GLM values directly in Click defaults: rejected because omitted flags would then change standard requests and the code could not distinguish omission from override.
- Ignore or reject inference flags outside GLM mode: rejected because the flags represent explicit tuning and their API meanings are not GLM-specific.
- Let server/model defaults supply unspecified GLM values: rejected because the feature requires deterministic GLM defaults independent of the selected model's embedded parameters.

## Decision 5: Use the existing CLI mechanism, not a new config store

**Decision**: Expose `--temperature`, `--top-p`, `--top-k`, `--repeat-penalty`, and `--num-predict`. Precedence for this feature is CLI override over mode default. Do not introduce YAML, TOML, or new environment variables because the OCR command has no existing inference configuration loader.

**Rationale**: The feature asks to use existing configuration or command-line mechanisms where applicable. CLI options are the applicable existing mechanism; a new configuration subsystem would expand scope and lifecycle substantially. The constructor-level override representation can accept a future config loader without redesigning request resolution.

**Alternatives considered**:

- Add a GLM YAML file: rejected because it creates a separate configuration store expressly outside the requested mode behavior.
- Treat Ollama model/Modelfile parameters as application configuration: rejected because explicit runtime defaults and CLI overrides are application request values and intentionally take precedence.

## Decision 6: Validate CLI input before any document processing

**Decision**: Reject unknown modes and non-numeric values through Click before engine creation. Apply these semantic ranges in both CLI and programmatic validation: `temperature >= 0`, `0 <= top_p <= 1`, `top_k >= 0`, `repeat_penalty > 0`, and `num_predict` is either `-1` (the documented unlimited value) or a positive integer. Merge explicit zero values with `is not None`, never truthiness.

**Rationale**: Early validation prevents partially processed batches. The ranges cover deterministic GLM defaults, allow meaningful zero boundaries, and preserve the documented `num_predict=-1` API value.

**Alternatives considered**:

- Rely entirely on remote-server validation: rejected because errors would occur only after discovery/rendering and could leave partial batch output.
- Require all values to be strictly positive: rejected because `temperature=0.0` is required and zero is meaningful for some sampling controls.

## Decision 7: Preserve retry, resume, output, and positional CLI behavior

**Decision**: Keep `archivatorium ocr INPUT_DIR OUTPUT_DIR`; the feature request's `<input>` is shorthand for the existing input operand, not a change to command arity. Preserve recursive PDF discovery, mirrored Markdown output, three-attempt backoff, recognized-page skipping, page ordering, headers, and error handling. Build the GLM request once per page so every retry is identical and isolated. Do not write mode metadata into Markdown.

**Rationale**: These behaviors are outside the mode-specific differences and are explicitly protected by backward compatibility. Existing outputs remain resumable and interoperable.

**Alternatives considered**:

- Accept a single PDF or make output optional: rejected as an unrelated CLI expansion.
- Add mode provenance to Markdown: rejected because it changes the output contract and resume files.
- Add retries for empty successful responses: rejected because current behavior does not do so and the feature does not require a new recovery policy.
