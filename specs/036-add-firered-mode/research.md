# Phase 0 Research: Add FireRed OCR Mode

## Decision 1: Extend the existing OCR mode-profile abstraction

**Decision**: Add FireRed as one immutable OCR mode profile alongside `standard` and `glm`, then resolve `--mode firered` to it before page processing begins.

**Rationale**: The current OCR engine already centralizes prompt selection, system-prompt presence, previous-page context, thinking control, and default inference settings in one profile. Adding a profile retains a single request-construction path for direct calls, normal runs, resume, and retries.

**Alternatives considered**:

- Add a FireRed-specific OCR engine subclass: rejected because rendering, retry, resume, and output behavior are identical and only request construction differs.
- Add a separate CLI command: rejected because it would duplicate the established input/output workflow and make mode selection less consistent.

## Decision 2: Make the supplied FireRed text the complete request prompt

**Decision**: Send exactly the user-supplied multiline FireRed prompt in one user message with the current page image; send no generic system prompt.

**Rationale**: The specification requires the exact supplied prompt. Adding the existing generic system prompt would add instructions not present in it and would make the effective prompt non-exact.

**Alternatives considered**:

- Keep the generic system prompt and add FireRed text as the user prompt: rejected because the request would contain additional instructions.
- Split the supplied text between system and user messages: rejected because it changes the supplied prompt's structure without a stated requirement.

## Decision 3: Enforce page isolation through the profile

**Decision**: Set FireRed's page-context policy to disabled. The existing message builder then refuses to append `last_text`, and the run loop supplies no preceding-page context for the profile.

**Rationale**: The current profile policy is checked both at request construction and while processing pages. This protects direct page calls, sequential multipage recognition, resume/missing-page recovery, and retries with one mechanism.

**Alternatives considered**:

- Suppress context only in the run loop: rejected because callers of single-page recognition could still add it.
- Clear the context string at selected call sites: rejected because it is error-prone and does not express the profile invariant.

## Decision 4: Preserve all unspecified FireRed behavior

**Decision**: FireRed retains the existing standard inference defaults, model selection, thinking behavior, rendering, retry policy, resume processing, output assembly, and recursive traversal. It changes only the complete prompt and the previous-page-context policy.

**Rationale**: The feature supplies no FireRed-specific inference or thinking requirements, and the specification expressly bounds changes to the mode-specific differences. Reusing standard defaults avoids undocumented behavioral changes.

**Alternatives considered**:

- Introduce FireRed sampling defaults: rejected because none were supplied and doing so would expand the feature's behavior.
- Disable thinking by analogy with GLM: rejected because that is a GLM-specific requirement, not a FireRed requirement.

## Decision 5: Extend the current CLI choice and tests

**Decision**: Add `firered` to the existing `--mode` choice and document it in the CLI contract. Add focused unit tests for the exact request, retry, multipage, and resumed flows, plus integration coverage for CLI selection and model independence.

**Rationale**: Click validates choices before any OCR work begins. The existing GLM tests establish the closest regression pattern for independent-page modes, enabling precise coverage without introducing a test framework or test data.

**Alternatives considered**:

- Parse free-form mode strings in the engine: rejected because invalid modes would no longer be rejected by the existing CLI validation path.
- Rely only on GLM tests: rejected because the FireRed prompt must match exactly and has different thinking/default behavior.
