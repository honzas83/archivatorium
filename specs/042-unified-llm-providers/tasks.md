---

description: "Dependency-ordered implementation tasks for unified Ollama and e-INFRA LLM providers"
---

# Tasks: Unified LLM Providers

**Input**: Design documents from `/specs/042-unified-llm-providers/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Tests are required because the specification makes unchanged Ollama behavior an absolute
release gate and defines provider contract, integration, privacy, retry, and live-smoke criteria.
Write each listed test before its corresponding implementation and confirm it fails for the intended
reason before changing production code.

**Organization**: Tasks are grouped by user story so Ollama compatibility, e-INFRA metadata, and
e-INFRA OCR can each be validated as a coherent increment.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel because it uses different files and does not depend on an unfinished task
- **[Story]**: Maps the task to User Story 1, 2, or 3
- Every task names the exact file or directory it changes or validates

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add the dependency, test classification, and secret-protection scaffolding required by
the feature without changing runtime behavior.

- [X] T001 Add the official OpenAI Python client dependency and register the opt-in `live_einfra` pytest marker in `pyproject.toml`
- [X] T002 [P] Add a root-anchored `/meta-api-key` exclusion and retain existing data exclusions in `.gitignore`
- [X] T003 [P] Create provider-test package scaffolding in `tests/contract/__init__.py` and `tests/live/__init__.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Define and test the provider-neutral types and configuration resolution that every user
story uses.

**CRITICAL**: No user-story implementation begins until this phase is complete.

- [X] T004 Write failing transport-independent contract tests for structured extraction, visible text responses, immutable retry semantics, and normalized errors in `tests/contract/test_llm_client.py`
- [X] T005 Implement typed provider identifiers, messages, attachments, reasoning directives, generation options, structured contracts, responses, capabilities, errors, transport protocol, and shared `LLMClient` facade in `archivatorium/services/llm_client.py`
- [X] T006 [P] Write failing provider/default/endpoint/model/option-resolution tests, including early validation and no-fallback assertions, in `tests/unit/test_llm_config.py`
- [X] T007 Implement provider selection, command-specific defaults, endpoint alias conflict checks, explicit-option tracking, and provider-independent connection configuration in `archivatorium/services/llm_factory.py`
- [X] T008 Export only the shared public LLM types and factory entry points from `archivatorium/services/__init__.py`

**Checkpoint**: Provider-neutral requests and validated connection configuration are usable without
either archival workflow constructing SDK-specific payloads.

---

## Phase 3: User Story 1 - Preserve Existing Ollama Runs (Priority: P1) - MVP

**Goal**: Route metadata, tagging, and OCR through the shared boundary while preserving every native
Ollama request, default, prompt, response rule, retry, traversal decision, log outcome, and generated
byte defined by the compatibility contract.

**Independent Test**: Run equivalent pre-refactor and post-refactor Ollama commands with captured
deterministic responses. Complete native request sequences must match exactly and generated files
must be byte-for-byte identical; the existing Ollama suite must pass without weakened assertions.

### Tests for User Story 1

- [X] T009 [P] [US1] Capture metadata/tagging native kwargs, prompt bytes, schema formatting, four-attempt validation correction, response cleanup, timeout, and exception behavior in `tests/unit/test_ollama_provider.py`
- [X] T010 [P] [US1] Extend every OCR profile, inference override, reasoning omission/value, response shape, empty result, retry/backoff, and timeout characterization in `tests/unit/test_ocr_engine.py` and `tests/unit/test_ocr_reasoning.py`
- [X] T011 [P] [US1] Capture metadata host/model/reasoning defaults and existing explicit-option behavior before refactoring in `tests/integration/test_metadata_command.py` and `tests/integration/test_model_think_cli.py`
- [X] T012 [P] [US1] Add deterministic golden tests for full Ollama call order, recursive metadata/OCR output bytes, resume, no-page-header behavior, and failed-output safety in `tests/integration/test_ollama_compatibility.py`

### Implementation for User Story 1

- [X] T013 [US1] Implement the native Ollama transport with unchanged structured and OCR timeouts, wire kwargs, response shapes, and provider-specific failure behavior in `archivatorium/services/ollama_client.py`
- [X] T014 [US1] Preserve the historical `OllamaClient` constructor and `extract_structured` facade while delegating through the shared contract in `archivatorium/services/ollama_client.py`
- [X] T015 [P] [US1] Change `MetadataProcessor` type dependencies to the shared structured-client protocol without altering prompts, call ordering, reconciliation, or persistence in `archivatorium/processor_metadata.py`
- [X] T016 [P] [US1] Change `TaggingService` type dependencies to the shared structured-client protocol without altering windowing, model/reasoning propagation, taxonomy rules, or quality checks in `archivatorium/services/tagging_service.py`
- [X] T017 [US1] Inject the shared text-generation client into `OCREngine` while preserving profile messages, image paths, native options, retries, normalization, traversal, temporary-file cleanup, and resume behavior in `archivatorium/ocr_engine.py`
- [X] T018 [US1] Resolve and construct the default Ollama client once per metadata or OCR command while retaining all legacy CLI spellings, environment precedence, model defaults, and output timing in `archivatorium/cli.py`
- [X] T019 [US1] Strengthen unchanged-command coverage for Ollama host/DigestAuth/environment precedence, recursive processing, partial credentials, and per-file continuation in `tests/integration/test_ocr_cli.py` and `tests/integration/test_metadata_command.py`

**Checkpoint**: Omitted-provider and explicitly selected Ollama runs are indistinguishable from the
pre-feature behavior under deterministic fixtures. Do not proceed if any compatibility assertion
requires weakening or snapshot replacement.

---

## Phase 4: User Story 2 - Use e-INFRA for Metadata and Tagging (Priority: P2)

**Goal**: Let users explicitly run metadata extraction and every tagging window through e-INFRA at
the default endpoint with `qwen3.8-27b`, shared structured validation, secure authentication, bounded
remote retries, and unchanged archival output contracts.

**Independent Test**: Process representative Markdown through a mocked e-INFRA transport and verify
authenticated JSON Schema requests, model/reasoning propagation across metadata and tagging calls,
existing Pydantic/downstream validation, actionable failures, no fallback, and no secret or reasoning
leakage in output or diagnostics.

### Tests for User Story 2

- [X] T020 [P] [US2] Add credential-file/environment precedence, whitespace, file type, permissions, unreadable/empty input, dynamic default, endpoint normalization, incompatible option, and redaction tests in `tests/unit/test_llm_config.py`
- [X] T021 [P] [US2] Write failing e-INFRA structured-request tests for Bearer auth, disabled SDK retries, JSON Schema format, 8,192-token allowance, reasoning mapping, visible JSON extraction, error classification, `Retry-After`, truncation, and empty output in `tests/unit/test_einfra_provider.py`
- [X] T022 [P] [US2] Write metadata CLI tests for additive provider options, help text, `qwen3.8-27b` defaults, model/base-URL overrides, early failures, and absence of implicit `OPENAI_API_KEY` or `meta-api-key` lookup in `tests/integration/test_llm_provider_cli.py`

### Implementation for User Story 2

- [X] T023 [US2] Implement the OpenAI-compatible e-INFRA transport foundation, safe client construction, structured Chat Completions translation, response normalization, remote error mapping, bounded retry, and redaction in `archivatorium/services/einfra_client.py`
- [X] T024 [US2] Implement secure e-INFRA credential resolution and instantiate the selected transport with no provider fallback in `archivatorium/services/llm_factory.py`
- [X] T025 [US2] Add `--llm-provider`, `--llm-base-url`, and `--llm-api-key-file` to metadata with provider-aware omitted-model resolution and pre-processing validation in `archivatorium/cli.py`
- [X] T026 [P] [US2] Verify metadata, final-date, and all tagging windows use one shared client, model, and reasoning choice without provider fields entering output in `tests/unit/test_metadata_reasoning.py` and `tests/unit/test_tagging_service.py`
- [X] T027 [US2] Wire the resolved e-INFRA shared client through metadata and tagging construction without provider branches in `archivatorium/cli.py`, `archivatorium/processor_metadata.py`, and `archivatorium/services/tagging_service.py`
- [X] T028 [US2] Add end-to-end mocked e-INFRA metadata/tagging success, validation retry, transient retry, permanent failure, per-document continuation, output-schema parity, no-fallback, and credential-redaction coverage in `tests/integration/test_llm_provider_cli.py`

**Checkpoint**: e-INFRA metadata and tagging complete through the same downstream models and document
rules as Ollama, while Ollama compatibility tests remain unchanged and green.

---

## Phase 5: User Story 3 - Use e-INFRA for OCR (Priority: P3)

**Goal**: Transcribe PDF pages through verified multimodal e-INFRA models using streamed visible
output while preserving the selected OCR profile, page context, normalization, recovery, resume,
layout, and sequential execution rules.

**Independent Test**: Run a synthetic multipage PDF with mocked streamed `qwen3.8-27b` responses,
interrupt after a completed page, resume, and verify capability lookup, image encoding, chunk order,
reasoning exclusion, retry identity, completed-page skipping, and final Markdown layout.

### Tests for User Story 3

- [X] T029 [P] [US3] Write failing transport tests for MIME-aware base64 data URLs, ordered content parts, reasoning mapping, 16,384-token allowance, chunk assembly, duplicate prevention, reasoning-delta exclusion, length exhaustion, and interrupted-stream buffer discard in `tests/unit/test_einfra_provider.py`
- [X] T030 [P] [US3] Write failing capability tests for one lookup per command, exact-model matching, multimodal acceptance, text-only/unknown/unavailable rejection before image transmission, and maximum-output validation in `tests/unit/test_llm_config.py`
- [X] T031 [P] [US3] Add OCR CLI tests for provider-aware defaults, endpoint alias agreement/conflict, credential/DigestAuth incompatibility, unsupported explicit sampling values, unlimited output, e-INFRA/GLM rejection, and validation before PDF discovery in `tests/integration/test_llm_provider_cli.py`

### Implementation for User Story 3

- [X] T032 [US3] Implement e-INFRA capability discovery/cache, multimodal validation, local-image encoding, streamed visible-text assembly, completion-state checks, and interrupted-stream retries in `archivatorium/services/einfra_client.py`
- [X] T033 [US3] Validate OCR mode and explicit generation options against the selected provider and capabilities before page processing in `archivatorium/services/llm_factory.py`
- [X] T034 [US3] Route OCR requests and complete responses through the shared client while keeping existing mode prompts, prior-page context, defensive `</think>` cleanup, page persistence, and per-file recovery in `archivatorium/ocr_engine.py`
- [X] T035 [US3] Add the common provider options and provider-aware e-INFRA model default to OCR, construct one command-scoped client, and retain legacy Ollama host/DigestAuth resolution in `archivatorium/cli.py`
- [X] T036 [US3] Add mocked multipage e-INFRA OCR tests for sequential calls, stream retry identity, partial-output rejection, page ordering, resume, completed-page skipping, no-page-header behavior, and byte-compatible Markdown layout in `tests/integration/test_ocr_cli.py` and `tests/integration/test_llm_provider_cli.py`

**Checkpoint**: e-INFRA OCR is complete and resumable using only visible streamed output; every
Ollama OCR profile still satisfies the immutable native compatibility baseline.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Finish opt-in live validation, user guidance, privacy review, and constitutional quality
gates across all stories.

- [X] T037 [P] Add doubly opt-in, sequential, synthetic e-INFRA structured and short OCR/resume smoke tests that retain no request or response content in `tests/live/test_einfra_smoke.py`
- [X] T038 [P] Document provider selection, secure credentials, Qwen 3.8 defaults, metadata/OCR examples, option compatibility, authorization caveats, no-fallback behavior, and model availability in `README.md`
- [X] T039 [P] Reconcile executable examples, expected failures, secret-permission checks, and live-test opt-in instructions with the delivered CLI in `specs/042-unified-llm-providers/quickstart.md`
- [X] T040 Add regression coverage proving credentials, Authorization headers, provider diagnostics, private reasoning, and partial streams never enter logs or archival files in `tests/contract/test_llm_client.py` and `tests/integration/test_llm_provider_cli.py`
- [X] T041 Run `ruff check`, `ruff format --check`, `flake8`, and strict `mypy` over `archivatorium/` and `tests/`, fixing only feature-related findings in those paths
- [X] T042 Run the complete default `pytest` and coverage suites, the focused Ollama compatibility suite, and the `specs/042-unified-llm-providers/quickstart.md` offline scenarios; document only genuine environmental blockers in `specs/042-unified-llm-providers/quickstart.md`

---

## Phase 7: Bounded OCR Concurrency

**Purpose**: Add explicitly requested throughput while retaining the default Ollama contract and
each PDF's sequential page-context and resume semantics.

- [X] T043 Back-propagate bounded independent-PDF concurrency into `spec.md`, `research.md`, `plan.md`, `data-model.md`, and provider contracts
- [X] T044 Add `--concurrency` to OCR with a default of one and an inclusive limit of four in `archivatorium/cli.py`
- [X] T045 Run independent PDF OCR jobs through a bounded executor while preserving the exact sequential path for omitted/default concurrency in `archivatorium/cli.py`
- [X] T046 Make e-INFRA capability lookup safe for a command-scoped client shared by parallel workers in `archivatorium/services/einfra_client.py`
- [X] T047 Add concurrency bound, observed parallelism, output isolation, and default compatibility coverage in `tests/integration/test_ocr_concurrency.py`
- [X] T048 Document concurrency scope, limits, single-PDF behavior, and examples in `README.md` and `specs/042-unified-llm-providers/quickstart.md`, then run feature and full regression gates

---

## Phase 8: Bounded Metadata Concurrency

**Purpose**: Extend the same explicit concurrency control to independent Markdown metadata jobs
without sharing mutable preflight counters or changing the default path.

- [X] T049 Extend `--concurrency` to metadata with the same default and inclusive limit in `archivatorium/cli.py`
- [X] T050 Add isolated preflight-snapshot workers sharing the command-scoped provider client and coordinator-side global counter reconciliation in `archivatorium/processor_metadata.py`
- [X] T051 Schedule matching Markdown metadata jobs through the bounded executor while retaining sequential dry-run and default behavior in `archivatorium/cli.py`
- [X] T052 Add observed metadata parallelism, bounds, default-path, and worker-isolation coverage in `tests/integration/test_metadata_concurrency.py` and `tests/unit/test_metadata_concurrency.py`
- [X] T053 Back-propagate metadata concurrency semantics into `spec.md`, `research.md`, `plan.md`, `data-model.md`, and provider contracts
- [X] T054 Document metadata concurrency, preflight snapshots, dry-run behavior, limits, and examples in `README.md` and `specs/042-unified-llm-providers/quickstart.md`
- [X] T055 Run focused metadata/Ollama compatibility tests and the complete default regression and coverage suite

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 - Setup**: No dependencies; start immediately.
- **Phase 2 - Foundational**: Depends on Phase 1 and blocks all user stories.
- **Phase 3 - User Story 1**: Depends on Phase 2. Its tests must capture the existing Ollama baseline
  before production refactoring begins.
- **Phase 4 - User Story 2**: Depends on Phase 2 and the shared/native compatibility boundary proven
  by User Story 1.
- **Phase 5 - User Story 3**: Depends on Phase 2, User Story 1's OCR compatibility boundary, and User
  Story 2's e-INFRA transport/error/authentication foundation.
- **Phase 6 - Polish**: Depends on every user story selected for delivery. Full release validation
  requires all three.
- **Phase 7 - Bounded OCR Concurrency**: Depends on the completed OCR provider boundary and immutable
  default-concurrency compatibility baseline.
- **Phase 8 - Bounded Metadata Concurrency**: Depends on the shared structured provider boundary,
  metadata preflight registry, and completed bounded executor pattern.

### User Story Dependency Graph

```text
Setup -> Foundation -> US1: Preserve Ollama
                         |
                         v
                    US2: e-INFRA metadata/tagging
                         |
                         v
                    US3: e-INFRA OCR
                         |
                         v
                      Polish
```

The stories are independently testable at their checkpoints, but implementation is intentionally
sequential because later stories reuse the already-proven shared boundary and remote transport.

### Within Each User Story

- Write and run the story's failing tests before its production-code tasks.
- Define provider-neutral models before transport or workflow integration.
- Complete transport translation before wiring the CLI and archival workflows.
- Validate a story independently and rerun the full Ollama compatibility suite before its checkpoint.
- Commit each completed task or tightly coupled test/implementation pair with only its named files;
  do not stage existing unrelated worktree changes or local credential/data files.

## Parallel Opportunities

### User Story 1

After Phase 2, the four characterization areas can be prepared in parallel before T013:

```text
T009: Structured Ollama request characterization
T010: OCR profile and retry characterization
T011: Metadata CLI resolution characterization
T012: Deterministic integration golden baseline
```

After T014, T015 and T016 can proceed in parallel because they migrate distinct consumers.

### User Story 2

After User Story 1, T020, T021, and T022 can be written in parallel. After T025, T026 can run while
T027 integrates the CLI construction path, provided no shared-file edits overlap.

### User Story 3

After User Story 2, T029, T030, and T031 can be written in parallel. Implementation then proceeds in
order from transport (T032), through validation (T033), workflow (T034), CLI (T035), and integration
(T036).

### Polish and Concurrency

T037, T038, and T039 can proceed in parallel after the implementation stories. T040-T042 close the
initial provider work. T043-T048 form a later ordered increment because tests depend on the public
CLI and bounded executor design.

## Implementation Strategy

### MVP First: Compatibility-Preserving Shared Boundary

1. Complete Setup and Foundational phases.
2. Complete User Story 1, capturing the baseline before modifying production code.
3. Stop and verify complete native request equality, deterministic byte-identical outputs, and the
   unmodified existing Ollama suite.
4. Treat this as the minimum safe architectural increment; do not release provider refactoring that
   fails the compatibility checkpoint.

### Incremental Delivery

1. **Foundation + US1**: Establish one client boundary with provably unchanged Ollama behavior.
2. **US2**: Add authenticated e-INFRA structured metadata and tagging with no archival-schema change.
3. **US3**: Extend the same remote transport to capability-checked streamed OCR and resume.
4. **Polish**: Add opt-in live checks, user documentation, privacy tests, and all quality gates.
5. **OCR Concurrency**: Add opt-in bounded parallelism across independent PDFs without changing the
   default path or per-PDF page semantics.
6. **Metadata Concurrency**: Apply the same bounded option across independent Markdown documents
   using isolated preflight snapshots and sequential per-document model stages.

### Validation Discipline

- Run the focused Ollama compatibility suite after every production task from T013 onward.
- Never update a golden request or output merely to match refactored behavior; restore the baseline
  unless the user explicitly amends the specification.
- Keep all automated remote tests mocked and deterministic. Live tests require both `-m live_einfra`
  and `ARCHIVATORIUM_RUN_EINFRA_LIVE=1` and use only synthetic data.
- Keep model stages within each document sequential, cap explicitly requested independent-document
  concurrency at four, and never add automatic provider fallback.

## Notes

- `[P]` tasks operate on distinct files or independent test areas and have no dependency on another
  incomplete task in the same phase.
- `[US1]`, `[US2]`, and `[US3]` provide traceability to the three specification stories.
- The repository already contains unrelated modified tests and untracked local files. Inspect status
  before every commit and stage only paths named by the completed task.
- `meta-api-key` is local validation material: protect it, ensure the root ignore rule applies, and
  never commit or copy its contents into fixtures, logs, or documentation.
