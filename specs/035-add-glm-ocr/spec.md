# Feature Specification: Add GLM OCR Mode

**Feature Branch**: `035-add-glm-ocr`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Add an explicitly selected `glm` OCR mode optimized for GLM-OCR, with its native prompt, independent page recognition, disabled reasoning, GLM-specific configurable inference defaults including a wider repetition lookback, independent model selection, and no changes to existing OCR behavior when the mode is not selected."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run OCR in GLM Mode (Priority: P1)

As a user processing documents with GLM-OCR, I want to select a dedicated GLM mode explicitly so that each page is recognized with the prompt and inference behavior expected by that OCR model family.

**Why this priority**: This is the core value of the feature: users can opt into GLM-optimized recognition without replacing or altering the established OCR workflow.

**Independent Test**: Run `archivatorium ocr <input> --mode glm` on a multipage document and verify that every page recognition request uses the exact prompt `Text Recognition:`, has reasoning disabled, uses the GLM defaults, and contains no OCR text from another page.

**Acceptance Scenarios**:

1. **Given** a valid multipage input and no inference overrides, **When** the user runs `archivatorium ocr <input> --mode glm`, **Then** every page is recognized independently using the exact prompt `Text Recognition:` with reasoning disabled and the GLM default inference values.
2. **Given** a document whose previous page has already been recognized, **When** the next page is recognized in GLM mode, **Then** the request contains no previous-page OCR text or other page-derived textual context.
3. **Given** an interrupted GLM-mode run with one page requiring recognition on resume, **When** the user resumes processing in GLM mode, **Then** that page is recognized without using the OCR of any neighboring page as context.

---

### User Story 2 - Select Model Independently (Priority: P2)

As a user, I want OCR mode and model selection to remain separate choices so that I can use GLM prompting and inference behavior with the specific installed model I choose.

**Why this priority**: Model availability and model naming vary between installations; selecting GLM mode must not silently force or replace the user's model choice.

**Independent Test**: Run GLM mode with an explicit `--model` value and verify that the chosen model is used while all GLM-mode prompt, reasoning, page-isolation, and inference behaviors remain active.

**Acceptance Scenarios**:

1. **Given** GLM mode and an explicit model selection, **When** OCR runs, **Then** the selected model is used and GLM-mode behavior remains unchanged.
2. **Given** GLM mode without an explicit model selection, **When** OCR runs, **Then** the existing model-selection default is used without the mode substituting a model.

---

### User Story 3 - Override GLM Inference Defaults (Priority: P3)

As an advanced user, I want the GLM inference defaults to be configurable through the OCR command's existing command-line parameter mechanism so that I can tune recognition for a particular collection without losing the GLM prompt and independent-page behavior.

**Why this priority**: The provided defaults should work for normal GLM-OCR use, while existing tuning workflows must remain available for exceptional documents and environments.

**Independent Test**: Supply a non-default value through each supported command-line inference option and verify that it takes precedence for the selected setting while all unspecified settings retain their GLM defaults.

**Acceptance Scenarios**:

1. **Given** GLM mode and one supported inference value overridden on the command line, **When** OCR runs, **Then** that value is used and every other unspecified inference value retains its GLM default.
2. **Given** GLM mode and all six supported inference values supplied on the command line, **When** OCR runs, **Then** all six explicit values are used instead of their GLM defaults.
3. **Given** an explicit valid zero value for a setting that permits zero, **When** OCR runs in GLM mode, **Then** zero is retained as the override rather than treated as an omitted value.
4. **Given** GLM mode without a `repeat_last_n` override, **When** OCR runs, **Then** the request checks the most recent 512 tokens for repetition to reduce duplication of longer OCR passages.

---

### User Story 4 - Preserve Existing OCR Behavior (Priority: P1)

As an existing user, I want standard OCR commands to behave exactly as before so that current scripts, prompts, context handling, defaults, and outputs do not change.

**Why this priority**: Backward compatibility is essential because GLM mode is an opt-in specialization rather than a replacement for the current OCR behavior.

**Independent Test**: Run representative existing OCR commands without `--mode glm` and compare their selected model, prompts, inference values, reasoning behavior, previous-page context handling, and output behavior with the pre-feature baseline.

**Acceptance Scenarios**:

1. **Given** an existing valid OCR invocation with no mode option, **When** it is run after this feature is introduced, **Then** it uses standard mode with the same behavior and defaults as before the feature.
2. **Given** an explicit `--mode standard`, **When** OCR runs, **Then** it behaves identically to omitting the mode option.
3. **Given** an unsupported mode value, **When** the user starts OCR, **Then** the command rejects the value with a clear error before recognizing any page.

### Edge Cases

- A single-page document in GLM mode is processed with the same page-isolation rules as each page of a multipage document.
- The first page and any resumed, missing, or retried page in GLM mode receive no text recognized from another page.
- Empty or failed recognition output may be retried according to existing OCR recovery behavior, but each GLM-mode retry remains independent and reasoning stays disabled.
- An override of `0`, `0.0`, or another boundary value is treated as an explicit value rather than as an absent setting, provided it is valid for that setting.
- Invalid inference override values are rejected with a clear error before page recognition begins.
- Selecting GLM mode must not change output naming, page ordering, resume detection, or input traversal behavior.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The OCR command MUST accept an explicitly selected GLM mode through `archivatorium ocr <input> --mode glm`.
- **FR-002**: Omitting `--mode` or explicitly selecting `--mode standard` MUST preserve all pre-existing OCR behavior, including prompting, inference defaults, reasoning behavior, previous-page context handling, model selection, resume behavior, and output structure.
- **FR-003**: Every page recognition request in GLM mode MUST use the exact native prompt `Text Recognition:`.
- **FR-004**: Every page recognition request in GLM mode MUST disable model thinking or reasoning.
- **FR-005**: In GLM mode, every page MUST be recognized independently; no request may include recognized text or textual context derived from any previous, next, or otherwise neighboring page.
- **FR-006**: FR-005 MUST apply to initial processing, resumed processing, missing-page recovery, and retries.
- **FR-007**: GLM mode MUST use the following inference defaults when the corresponding setting is not overridden: `temperature = 0.0`, `top_p = 0.00001`, `top_k = 1`, `repeat_penalty = 1.1`, `repeat_last_n = 512`, and `num_predict = 8192`.
- **FR-008**: Each GLM inference default MUST be overridable through the OCR command's existing command-line option mechanism.
- **FR-009**: A command-line inference override MUST take precedence over the selected mode's default for the same setting.
- **FR-010**: Overriding one inference setting MUST NOT change the effective values of other, unspecified inference settings.
- **FR-011**: OCR mode selection and model selection MUST remain independent: `--mode` controls prompting, reasoning, page-context behavior, and mode defaults, while `--model` selects the actual model.
- **FR-012**: Selecting GLM mode MUST NOT silently set, replace, or constrain the model selected by `--model` or by the existing model default.
- **FR-013**: The command MUST accept only `standard` and `glm` OCR mode values and reject unsupported values with a clear error before processing begins.
- **FR-014**: GLM mode MUST retain existing OCR behavior outside the mode-specific differences stated in FR-003 through FR-012, including input discovery, output formatting, page ordering, retries, and resume validation.

### Key Entities

- **OCR Mode Profile**: The explicitly selected recognition behavior for a run. It determines the prompt, reasoning state, page-context policy, and default inference values, but not the selected model.
- **Inference Settings**: The effective temperature, probability threshold, candidate limit, repetition penalty, repetition lookback window, and output-token limit used for a page. Each value records its effective source: command-line override or mode default.
- **Page Recognition Request**: A single page image combined with its mode-selected prompt, reasoning state, effective inference settings, and selected model. In GLM mode it has no textual context derived from other pages.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: In validation across single-page, multipage, resumed, missing-page, and retry scenarios, 100% of GLM-mode page recognitions use the exact prompt `Text Recognition:` with reasoning disabled.
- **SC-002**: In the same validation scenarios, 100% of GLM-mode page recognition requests contain no recognized text or textual context derived from another page.
- **SC-003**: With no overrides, 100% of observed GLM-mode page recognitions use all six specified default inference values, including `repeat_last_n=512`.
- **SC-004**: For each supported inference setting, command-line override tests produce the documented effective value and precedence in 100% of cases.
- **SC-005**: In all model-selection tests, the explicitly selected model is used without changing GLM-mode behavior, and selecting GLM mode never changes the model on its own.
- **SC-006**: All representative pre-existing OCR acceptance scenarios pass unchanged when mode is omitted or explicitly set to `standard`.
- **SC-007**: A user familiar with the existing OCR command can activate the optimized behavior by adding only `--mode glm`, with no other required command changes.

## Assumptions

- GLM mode is opt-in; `standard` is the default mode, and omitting the mode option selects the same behavior that existed before this feature.
- The existing OCR pipeline remains responsible for input discovery, rendering, output assembly, resume validation, retry decisions, and error reporting.
- “Disables thinking/reasoning” means the recognition request explicitly prevents the selected model from entering a reasoning mode when the inference provider supports that control; it does not merely omit reasoning text from the saved OCR output.
- “Previous page OCR as context” includes both direct insertion of the prior page's text and any prompt fragment derived from that text.
- The project has no existing OCR inference configuration-file loader; the six settings are therefore exposed through the existing command-line option mechanism, without introducing a separate configuration store.
- Invalid mode names and invalid inference values are reported before processing to avoid partially processed runs caused by input errors.
