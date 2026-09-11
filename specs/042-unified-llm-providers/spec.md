# Feature Specification: Unified LLM Providers

**Feature Branch**: `042-unified-llm-providers`

**Created**: 2026-09-11

**Status**: Draft

**Input**: User description: "Support the e-INFRA OpenAI-compatible endpoint with Qwen 3.8 through a unified LLM access boundary, with the absolute requirement that existing Ollama CLI use remains backward compatible and produces the same result in the LLM sense."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Preserve Existing Ollama Runs (Priority: P1)

As an existing archivatorium user, I can run the same metadata and OCR commands against Ollama and receive the same model instructions, inference behaviour, processing flow, and generated document results as before this feature.

**Why this priority**: Ollama is the established production path. Adding another provider is unacceptable if it changes existing model behaviour, output quality, resume behaviour, or automation compatibility.

**Independent Test**: Run the pre-feature and post-feature Ollama commands with identical inputs, CLI arguments, model responses, and filesystem state. The model request sequence and generated outputs must match exactly. In a live comparison using the same Ollama model and settings, no prompt, inference setting, retry rule, context rule, or output-processing change may be attributable to this feature; ordinary model nondeterminism is the only permitted source of variation.

**Acceptance Scenarios**:

1. **Given** an existing metadata command that omits all new provider options, **When** it runs after the feature is introduced, **Then** it selects Ollama and preserves the existing model, host, reasoning default, metadata prompt, tagging prompt, call sequence, retry behaviour, and generated output contract.
2. **Given** an existing OCR command using any supported OCR mode and inference overrides, **When** it runs after the feature is introduced, **Then** it sends the same system and user instructions, image, previous-page context, reasoning value, inference values, and retry sequence as before.
3. **Given** deterministic model responses supplied to equivalent pre-feature and post-feature Ollama runs, **When** metadata or OCR processing completes, **Then** the generated Markdown and related outputs are byte-for-byte identical.
4. **Given** existing Ollama environment settings, Digest authentication options, custom host usage, or explicit model selection, **When** the unchanged command is run, **Then** each setting retains its current precedence and meaning.
5. **Given** an existing failed, resumed, skipped, overwritten, or partially completed Ollama run, **When** the same command is repeated after the feature, **Then** file discovery, page recovery, metadata preflight, retry, and output decisions remain unchanged.

---

### User Story 2 - Use e-INFRA for Metadata and Tagging (Priority: P2)

As an archivatorium user with e-INFRA access, I can select e-INFRA for metadata and tagging so that archival Markdown is processed with the available Qwen 3.8 model while retaining the existing metadata, taxonomy, entity, and conceptual-tag output contracts.

**Why this priority**: Metadata and tagging are the principal structured-language workflows and can benefit from shared remote model capacity without requiring a local model installation.

**Independent Test**: Process a representative Markdown document using e-INFRA and `qwen3.8-27b`, then verify that all expected metadata and tag sections are valid, the selected endpoint receives authenticated requests, reasoning is applied as requested, and no provider-specific content appears in the archival output.

**Acceptance Scenarios**:

1. **Given** a valid e-INFRA credential and provider selection, **When** the user runs metadata extraction without an explicit model, **Then** the run uses the e-INFRA endpoint and `qwen3.8-27b`.
2. **Given** an explicit supported e-INFRA model, **When** metadata extraction and every tag-inference window run, **Then** all calls use that model and the same command-scoped reasoning choice.
3. **Given** a structured response that conforms to the requested metadata or tagging contract, **When** it is returned by e-INFRA, **Then** it is validated and processed through the same downstream document rules used for Ollama.
4. **Given** a response that is truncated, empty, malformed, or temporarily unavailable, **When** it is handled, **Then** the user receives bounded retries where safe and a clear failure that identifies the affected document without exposing credentials or private reasoning.

---

### User Story 3 - Use e-INFRA for OCR (Priority: P3)

As an archivatorium user with e-INFRA access, I can use the multimodal Qwen 3.8 model to transcribe PDF pages while preserving the current OCR mode prompts, recursive traversal, page headers, recovery behaviour, and output normalization.

**Why this priority**: Remote OCR completes provider coverage across all model-dependent workflows, but it depends on the shared provider selection, authentication, reasoning, and response behaviour established by the earlier stories.

**Independent Test**: Process a small multipage PDF through e-INFRA using `qwen3.8-27b` and the Qwen 3.8 OCR mode, interrupt and resume the run, and confirm that page ordering, saved transcription, context handling, retry behaviour, and skipped completed pages satisfy the existing OCR contract.

**Acceptance Scenarios**:

1. **Given** a valid e-INFRA credential and a multimodal model, **When** an OCR page is processed, **Then** the current page image and the selected OCR mode instructions reach the model and only the visible transcription is written.
2. **Given** the Qwen 3.8 OCR mode and a command-scoped reasoning choice, **When** one or more pages are processed or retried, **Then** every attempt uses the same selected reasoning level and sufficient output allowance for both reasoning and transcription.
3. **Given** a long-running e-INFRA response, **When** output is produced incrementally, **Then** the complete visible response is assembled without leaking private reasoning or altering the final Markdown layout.
4. **Given** an interrupted PDF run with valid completed page output, **When** the run resumes, **Then** completed pages are skipped and missing pages are processed exactly once apart from bounded retries.

### Edge Cases

- The selected e-INFRA credential file is missing, empty, unreadable, or contains surrounding whitespace.
- The e-INFRA service rejects the credential, model name, request format, or requested capability.
- A text-only model is selected for OCR, or an unavailable model is selected for any workflow.
- A response consumes its entire output allowance in reasoning and returns no visible result.
- A structured response is valid JSON but does not satisfy the requested metadata or tagging contract.
- A streamed response ends early, repeats a fragment, contains reasoning separately from visible content, or reports failure after partial output.
- The service returns a timeout, rate-limit response, transient server failure, or permanent client error.
- The user supplies Ollama-only authentication or inference options while selecting e-INFRA.
- The user supplies e-INFRA credentials while retaining the default Ollama provider.
- A base endpoint is supplied with or without a trailing slash.
- An unchanged Ollama command relies on environment variables rather than explicit options.
- The local Ollama server supports only the existing native request behaviour and not an alternate compatibility interface.
- The input contains protected or sensitive archival material for which remote processing has not been authorized.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide one shared, provider-neutral model-access boundary for metadata extraction, tag inference, and OCR.
- **FR-002**: The system MUST support Ollama and the e-INFRA endpoint at `https://llm.ai.e-infra.cz/v1/` as explicitly selectable model providers.
- **FR-003**: Ollama MUST remain the default provider when the user does not select a provider.
- **FR-004**: Every metadata and OCR CLI invocation that was valid before this feature MUST remain valid with the same argument and environment-variable meaning.
- **FR-005**: For unchanged Ollama invocations, the system MUST preserve the currently resolved host, model defaults, credentials, OCR mode, prompts, message order and content, image input, previous-page context, reasoning value and type, inference settings, call ordering, retry behaviour, timeouts, response normalization, recursive traversal, resume decisions, and generated output format.
- **FR-006**: With deterministic model responses and equivalent filesystem state, unchanged Ollama invocations MUST produce byte-for-byte identical generated outputs and the same externally observable logging and error outcome, excluding timestamps and measured durations.
- **FR-007**: Live Ollama compatibility MUST be judged by the absence of any feature-introduced change to model instructions or request semantics; ordinary nondeterministic variation from the same model is not a compatibility failure.
- **FR-008**: Provider support MUST NOT require metadata, tagging, or OCR workflows to construct provider-specific requests or interpret provider-specific responses.
- **FR-009**: Users MUST be able to select the provider, endpoint, model, credential source, and supported reasoning effort through consistent CLI concepts on both model-dependent commands.
- **FR-010**: Existing Ollama connection options MUST remain supported; any replacement option names MUST be additive aliases during this feature rather than removals or semantic changes.
- **FR-011**: When e-INFRA is selected and no endpoint is supplied, the system MUST use `https://llm.ai.e-infra.cz/v1/`.
- **FR-012**: When e-INFRA is selected and no model is supplied, the system MUST use the exact model identifier `qwen3.8-27b` for both metadata and OCR.
- **FR-013**: OCR prompt mode selection MUST remain independent of provider and model selection; selecting e-INFRA MUST NOT silently change the selected OCR mode.
- **FR-014**: The system MUST accept e-INFRA credentials from a designated environment variable or an explicitly selected credential file and MUST NOT require a credential value directly in the command line.
- **FR-015**: Credentials and private reasoning MUST NOT appear in generated documents, normal logs, error messages, progress output, or test fixtures.
- **FR-016**: The system MUST fail before processing source documents when e-INFRA is selected without a usable credential.
- **FR-017**: The system MUST reject provider-incompatible explicit options with a clear message rather than silently ignore them or change their meaning.
- **FR-018**: The system MUST represent disabled, low, medium, and high reasoning as shared user choices and preserve their intended meaning across providers.
- **FR-019**: Disabled reasoning MUST result in no requested reasoning for both supported providers, while each named reasoning level MUST be applied consistently to every governed call and retry.
- **FR-020**: The system MUST account for the fact that visible output and reasoning can share one output allowance and MUST distinguish output exhaustion from a valid empty result.
- **FR-021**: Metadata and tagging responses from either provider MUST be validated against the same existing structured data contracts before downstream processing.
- **FR-022**: OCR responses from either provider MUST expose only visible response text to the existing normalization and persistence flow.
- **FR-023**: The system MUST support image input through e-INFRA for models that advertise multimodal capability and MUST reject OCR use of a known text-only model before page processing where capability information is available.
- **FR-024**: The system MUST support complete assembly of incrementally delivered e-INFRA responses so long-running requests can finish without changing the final visible content.
- **FR-025**: Retry decisions MUST distinguish correctable output validation failures and temporary service failures from permanent authentication, capability, model, and request errors.
- **FR-026**: Retries MUST be bounded, retain identical provider, model, reasoning, prompt, and image semantics, and respect any documented service retry delay.
- **FR-027**: The system MUST NOT switch providers automatically after a failure or send source content to a provider the user did not explicitly select.
- **FR-028**: A failed or interrupted remote request MUST NOT leave a page or document marked complete unless its existing output validity rules are satisfied.
- **FR-029**: The system MUST retain the existing limit of sequential processing by default and MUST prevent future remote concurrency from exceeding four requests per account unless the service documents a different limit.
- **FR-030**: User documentation MUST include provider selection, secure credential setup, the initial Qwen 3.8 model, metadata and OCR examples, supported and incompatible options, model availability caveats, and the prohibition on committing credentials.
- **FR-031**: Live-provider validation MUST be opt-in, use local non-versioned data and credentials, and remain separate from the default automated test suite.
- **FR-032**: The feature MUST NOT change the output schemas, canonical tag model, topic taxonomy rules, metadata reconciliation rules, OCR prompts, or archival file layout.

### Key Entities

- **Provider Selection**: The explicit choice of model service for a command. It determines connection, authentication, capability, and request translation while leaving the archival workflow unchanged.
- **Model Connection**: The resolved provider, endpoint, model identifier, credential source, authentication method, and timeout policy for one run.
- **Model Request**: A provider-neutral description of ordered messages, optional images, structured-result expectations, reasoning choice, output allowance, and supported inference choices.
- **Model Response**: The visible content, completion state, usage information, and failure state returned to the calling workflow without exposing private reasoning.
- **Provider Capability**: A declared or discovered ability such as chat, structured results, multimodal input, reasoning control, or incremental response delivery.
- **Ollama Compatibility Baseline**: The pre-feature observable contract for unchanged Ollama commands, including CLI resolution, model requests, processing decisions, and generated outputs.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: One hundred percent of existing automated Ollama metadata, tagging, OCR, reasoning, retry, resume, and CLI tests pass without weakening their assertions.
- **SC-002**: Across golden compatibility fixtures with deterministic model responses, pre-feature and post-feature Ollama runs produce identical model-call sequences and byte-for-byte identical generated files in 100% of cases.
- **SC-003**: A user with a valid e-INFRA credential can complete metadata and tagging for a representative document using `qwen3.8-27b` in one command and receive output accepted by all existing downstream validators.
- **SC-004**: A user with a valid e-INFRA credential can complete and resume a multipage Qwen 3.8 OCR run with 100% of completed pages retained in correct order and no private reasoning stored in output.
- **SC-005**: Every missing credential, unsupported explicit option, unavailable model, incompatible capability, authentication failure, truncated response, and invalid structured response in the acceptance suite ends with a specific actionable outcome and zero credential disclosure.
- **SC-006**: All provider-independent acceptance tests exercise metadata, tagging, and OCR without requiring those workflows to know which supported provider produced the response.
- **SC-007**: Existing users can run their previously documented Ollama commands without adding or renaming any option, and all such compatibility scenarios complete with no feature-caused change in model semantics.
- **SC-008**: No credential file, credential value, live archival sample, or live-provider output is added to version control by the feature validation workflow.

## Assumptions

- The first supported e-INFRA model is the exact, currently available identifier `qwen3.8-27b`; later model additions are configuration choices rather than new workflow implementations.
- Exact e-INFRA model identifiers may be retired or replaced, so availability failures are reported clearly and the selected model remains user-overridable.
- The existing `False`, `low`, `medium`, and `high` reasoning choices remain the public contract. Their provider-specific representation is invisible to users.
- Ollama keeps its current default models independently for metadata and OCR. The e-INFRA provider has its own default model.
- Existing OCR modes and their prompts remain independent from the selected provider and model.
- The current processing flow is sequential. No throughput benchmarking or new parallel processing is included in this feature.
- Automatic failover is excluded because it could transmit archival content to an unselected service and would make reproducibility harder.
- Users are responsible for confirming that remote processing is authorized for their source material. Documentation will distinguish local processing from e-INFRA processing and warn against sending unauthorized protected material.
- The repository-root `meta-api-key` file may be used for local opt-in validation only after it is excluded from version control and protected by restrictive filesystem permissions; it is not a committed project asset or a default credential location.
- Clean, interlinking, indexing, and other non-model workflows are outside this feature except for confirming that their inputs remain compatible.

