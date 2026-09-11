# Implementation Plan: Unified LLM Providers

**Branch**: `042-unified-llm-providers` | **Date**: 2026-09-11 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/042-unified-llm-providers/spec.md`

## Summary

Add the e-INFRA OpenAI-compatible service as an explicit provider for metadata, tagging, and OCR,
initially using `qwen3.8-27b`. Introduce one application-facing LLM client and provider-neutral
request/response model, backed by separate native Ollama and OpenAI-compatible transports. Preserve
the native Ollama wire contract, CLI defaults, environment precedence, prompts, options, retries,
timeouts, response cleanup, traversal, resume behavior, logging outcomes, and generated files. Lock
that behavior with characterization and deterministic golden tests before migrating callers.

## Technical Context

**Language/Version**: Python 3.12 (`requires-python = ">=3.12"`)

**Primary Dependencies**: Click CLI, Pydantic, PyYAML, native `ollama>=0.6.1`, official OpenAI
Python client for e-INFRA, httpx, pdf2image, PyPDF2, pytest/pytest-cov

**Storage**: Existing filesystem Markdown/PDF vault output and YAML taxonomy/tag configuration;
environment or local file credential input; no database or output-schema changes

**Testing**: pytest/pytest-cov, ruff lint/format, flake8 with cognitive-complexity checks, strict mypy,
provider contract tests, deterministic Ollama compatibility fixtures, opt-in live e-INFRA smoke tests

**Target Platform**: macOS and Linux command-line environments with either an accessible Ollama
service or authorized HTTPS access to e-INFRA

**Project Type**: Single Python CLI application

**Performance Goals**: Preserve current sequential Ollama behavior when concurrency is omitted;
allow one through four independent PDF OCR or Markdown metadata jobs per command; make no more than
one capability lookup per e-INFRA OCR run even under parallel startup; assemble streamed OCR output
without duplicate or missing visible chunks

**Constraints**: Ollama remains the default; unchanged Ollama invocations must retain native request
semantics and deterministic output bytes; no automatic provider fallback; credentials and private
reasoning never enter logs or artifacts; provider validation occurs before document processing;
remote output budgets include reasoning tokens; existing output schemas and prompts remain unchanged;
pages within one PDF remain sequential so previous-page context is never weakened

**Scale/Scope**: Two model-dependent CLI commands, one shared client/factory, two provider
transports, three LLM consumers, four OCR profiles, existing structured metadata/tag schemas,
focused contract/unit/integration coverage, and separately gated live validation

## Constitution Check

*GATE: Passed before Phase 0 research and re-checked after Phase 1 design.*

- **I. Quality-Driven Python Development — PASS**: The feature remains Python 3.12 and defines
  characterization, contract, unit, integration, live-smoke, lint, format, complexity, typing, and
  coverage validation. Shared provider logic is decomposed into typed, testable units.
- **II. CLI-First Interface — PASS**: Provider, endpoint, credential source, model, and reasoning are
  exposed through additive POSIX-style options on the existing `metadata` and `ocr` commands.
- **III. Recursive Directory Processing — PASS**: Discovery, mirroring, processing order, and resume
  rules are preserved. Provider selection changes only model access.
- **IV. Data Isolation — PASS**: Automated tests use synthetic temporary data. Live inputs and
  outputs remain under gitignored `data/042-unified-llm-providers/`; credentials are excluded from
  version control and never embedded in fixtures.
- **V. Atomic Git Workflow — PASS**: Implementation begins with compatibility tests and proceeds in
  provider/client/caller increments. Tasks must stage only their named feature paths and preserve the
  existing unrelated modified tests and untracked local files.
- **Post-design re-check — PASS**: The data model and contracts introduce no storage service,
  alternate output model, new command, automatic failover, or change to recursive processing. The
  dual transport is justified by the absolute native-Ollama compatibility requirement and remains
  behind one application-facing boundary.

## Project Structure

### Documentation (this feature)

```text
specs/042-unified-llm-providers/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── cli.md
│   ├── llm-client.md
│   └── ollama-compatibility.md
└── tasks.md                         # Created by /speckit-tasks
```

### Source Code (repository root)

```text
archivatorium/
├── cli.py                           # Add provider options and build one resolved client
├── ocr_engine.py                    # Consume provider-neutral text generation
├── processor_metadata.py            # Depend on the shared structured client contract
├── services/
│   ├── llm_client.py                # Shared facade, request/response/errors, structured validation
│   ├── llm_factory.py               # Provider-aware defaults, credential and option validation
│   ├── ollama_client.py             # Native Ollama transport and compatibility facade
│   ├── einfra_client.py             # OpenAI-compatible transport, streaming and capability lookup
│   └── tagging_service.py           # Depend on the shared structured client contract
└── utils/
    └── model_think.py               # Provider-neutral public reasoning type

tests/
├── contract/
│   └── test_llm_client.py            # Shared facade behavior across fake transports
├── integration/
│   ├── test_llm_provider_cli.py      # Provider/default/auth/error matrix for both commands
│   ├── test_metadata_command.py      # Existing Ollama and new provider construction
│   ├── test_model_think_cli.py       # Shared CLI value and transport mappings
│   ├── test_ocr_cli.py               # OCR provider selection and unchanged Ollama behavior
│   └── test_ollama_compatibility.py  # Deterministic request/output golden baseline
├── live/
│   └── test_einfra_smoke.py          # Explicitly enabled synthetic live checks
└── unit/
    ├── test_llm_config.py            # Resolution, credentials and incompatible options
    ├── test_ollama_provider.py        # Exact native request and timeout behavior
    ├── test_einfra_provider.py        # Auth, schema, vision, reasoning, streaming and errors
    ├── test_metadata_reasoning.py     # Existing propagation through shared facade
    ├── test_ocr_engine.py             # Existing profiles/retry/resume invariants
    ├── test_ocr_reasoning.py          # Mode-specific reasoning remains unchanged
    └── test_tagging_service.py        # Existing calls through shared facade

README.md                              # Provider setup, secure credentials and examples
.gitignore                             # Root-anchor the local meta-api-key exclusion
pyproject.toml                         # OpenAI client dependency and live-test marker
```

**Structure Decision**: Keep the single CLI package. `LLMClient` is the only model-access boundary
visible to metadata, tagging, and OCR. It composes a provider transport rather than forcing both
services through one wire protocol. `OllamaClient` remains as a compatibility facade during the
migration so existing internal callers and tests can move without changing native Ollama behavior.

## Implementation Design

### Characterize Ollama before abstraction

- Capture complete native structured and OCR request kwargs, timeout construction, model/host/auth
  precedence, response parsing, retry counts and prompt mutation before changing callers.
- Cover every OCR profile, prior-page policy, explicit override, empty response, dictionary/object
  response, retry, page resume, no-page-header, and deterministic output rendering.
- Treat existing assertions as a floor. Do not update snapshots to accept a newly changed request.

### Shared client and provider transports

- Define immutable provider-neutral connection, message, image, generation-option, structured-result,
  visible-response, capability, and normalized-error types.
- Keep structured prompt composition, JSON cleanup, Pydantic validation, and validation retries in
  the shared facade while preserving the current Ollama bytes and four-attempt validation behavior.
- Keep provider wire shapes entirely inside transports. The Ollama transport uses native
  `ollama.Client.chat`; e-INFRA uses OpenAI-compatible Chat Completions.
- Inject one resolved client into each command run. `MetadataProcessor`, `TaggingService`, and
  `OCREngine` neither construct SDK clients nor parse provider responses.

### Configuration and credentials

- Add `--llm-provider`, `--llm-base-url`, and `--llm-api-key-file` consistently to both model
  commands. Retain `--host` as an endpoint alias; conflicting endpoint values fail before work.
- Resolve omitted models by provider and command: retain `gemma4:31b` for Ollama metadata and
  `qwen3.5:9b` for Ollama OCR; use `qwen3.8-27b` for either e-INFRA workflow.
- Preserve existing Ollama environment and DigestAuth precedence exactly. For e-INFRA, an explicit
  key file overrides `E_INFRA_API_TOKEN`; do not read a repository key implicitly or consume
  `OPENAI_API_KEY`.
- Strip surrounding credential whitespace, reject missing/empty/unreadable or group/world-readable
  key files, redact secret-bearing objects, and validate the complete configuration before output
  directories, templates, preflight scans, PDF rendering, or remote calls.

### Provider-specific semantics

- Map public reasoning `False` to native Ollama boolean false and e-INFRA `none`; pass named levels
  unchanged. Preserve profile-specific omission and GLM false behavior.
- Preserve all Ollama options, timeouts, retries, logging, and `stream=False` exactly.
- For e-INFRA, support temperature, top-p, positive output limits, structured JSON Schema, base64
  image content, visible-content extraction, and streamed OCR aggregation. Reject unsupported
  explicit top-k/repetition settings, unlimited output, and the GLM profile instead of dropping
  required semantics.
- Use initial e-INFRA allowances of 8,192 tokens for structured calls and 16,384 for OCR. Detect
  exhausted output and empty visible content distinctly; never save partial streamed OCR.
- Query and cache e-INFRA model capabilities once when OCR needs multimodal validation. If capability
  data is unavailable, fail safely rather than transmit images to a model not verified as multimodal.

### Errors, retries, and privacy

- Normalize configuration, authentication, invalid request, unknown model, unsupported capability,
  rate limit, transient service, truncated response, empty response, stream interruption, and
  structured-validation failures without leaking raw headers, secrets, or private reasoning.
- Retry only correctable validation failures and transient e-INFRA failures, honoring a bounded
  retry delay. Permanent errors fail immediately. Every retry retains provider, model, prompts,
  images, reasoning, and inference semantics.
- Do not unify retry behavior by changing Ollama: structured validation retains four total attempts;
  OCR retains three attempts with current backoff and per-file continuation.
- Never fail over between providers. Keep concurrency at one by default. When explicitly set above
  one, schedule independent PDFs through a bounded thread pool capped at four while retaining one
  sequential page chain and one resume/output boundary per PDF.
- Share the command-scoped e-INFRA client across workers and serialize first capability discovery so
  simultaneous first pages do not duplicate model-list requests.
- For metadata, complete preflight once, then give each parallel document an isolated snapshot of
  the vocabulary and counters. Keep metadata, conditional date extraction, tagging windows,
  validation, and persistence sequential within that document. Reconcile each successful output
  into the global counters on the coordinator thread after the worker completes.

### Validation strategy

- Run new Ollama characterization tests before production refactoring, then after every migration
  step. Compare full request sequences and output bytes for deterministic responses.
- Test shared behavior with fake transports, then test each provider translation independently.
- Cover CLI option sources, dynamic defaults, aliases/conflicts, credential permissions/redaction,
  incompatible options, early failure, model/reasoning propagation, and absence of fallback.
- Cover concurrency bounds, observed maximum simultaneous jobs, independent output, per-file failure
  continuation, and unchanged omitted-option Ollama behavior.
- Verify parallel metadata processors share the resolved backend client but do not share mutable
  preflight counters, and verify successful outputs update the global registry afterward.
- Keep live e-INFRA tests doubly opt-in, sequential, synthetic, and outside normal test execution.
  Validate one structured metadata/tagging flow and one short Qwen 3.8 OCR/resume flow without
  snapshotting model output.
- Finish with all constitutional quality gates and document any pre-existing environmental blockers
  without weakening the feature tests.

## Complexity Tracking

No constitution violations require justification. The two provider transports are ordinary scoped
integration components behind one application boundary, not additional projects or user workflows.
