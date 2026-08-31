# Phase 0 Research: Qwen 3.8 Markdown OCR Profile

## Decision 1: Add a dedicated Qwen 3.8 mode

**Decision**: Add `qwen38` to the existing mode selector and resolve it to a new immutable profile with dedicated prompts, previous-page context enabled, and high reasoning. Keep model selection independent and leave the default model identifier unchanged.

**Rationale**: The supplied diff is experimental prompt inspiration, while the required product behavior is a separately selectable mode. A dedicated profile isolates the experiment and guarantees that standard, GLM, and FireRed requests remain unchanged. It can still reuse the existing message and request lifecycle without duplicating implementation logic.

**Alternatives considered**:

- Modify standard mode: rejected because the user requires standard behavior to remain unchanged.
- Detect Qwen from the model string: rejected because model names are operator-defined and the mode must be explicitly selectable.
- Change the default model to Qwen 3.8: rejected because mode and model selection remain independent and the specification keeps the default unchanged.

## Decision 2: Replace overlapping instructions with one ordered output contract

**Decision**: Use one concise system prompt with a role sentence, a direct transcription task, and an ordered set of output rules. Use a one-sentence user prompt that references that contract. State source fidelity once, Markdown-only structure once, paragraph joining once, table behavior once, spacing normalization once, and blank/unreadable behavior once.

**Rationale**: The current system prompt asks the model both to preserve spatial indentation and to produce single-line paragraphs, while the user prompt repeats layout fidelity. The supplied diff removes part of this conflict but retains duplicated fidelity language. A single ordered contract gives the model a clearer priority hierarchy and makes exact request behavior testable.

**Alternatives considered**:

- Keep the current prompt and append more rules: rejected because contradictions and duplication would remain.
- Put all rules in the user message: rejected because the new profile uses a stable system-level behavior contract and appends previous-page context to the user message.
- Split rules across several prompts: rejected because the current request needs one coherent instruction hierarchy.

## Decision 3: Prohibit page-layout indentation while allowing Markdown-required whitespace

**Decision**: Require every top-level block to start at column one and prohibit copied page margins or visual-layout indentation. Permit indentation only where Markdown syntax requires nested list structure or inside a fenced literal block.

**Rationale**: An absolute ban on indentation conflicts with valid nested Markdown lists and fixed-width fallback content. The user's underlying problem is globally indented, typewriter-like OCR output, which is addressed by banning layout-derived indentation while retaining syntactically meaningful Markdown whitespace. Existing response normalization remains a defensive cleanup boundary for shared global indentation.

**Alternatives considered**:

- Ban every leading space: rejected because it makes nested lists and literal fixed-width content impossible to represent faithfully.
- Preserve all source indentation: rejected because it recreates the malformed Markdown this feature is intended to prevent.
- Add a deterministic indentation rewriter: rejected because it cannot reliably distinguish prose, nested lists, tables, and literal blocks.

## Decision 4: Preserve typewriter headings without Markdown styling

**Decision**: Instruct Qwen 3.8 mode to keep visually supported headings as plain text on their own lines and never generate Markdown heading, bold, or italic markers from capitalization, spacing, underlining, position, or other typewriter layout cues.

**Rationale**: The target text was produced on typewriters and does not contain Markdown styling. Adding ATX or emphasis markers invents characters and formatting absent from the document; preserving a separate plain-text line retains the visible heading boundary without editorial markup.

**Alternatives considered**:

- Use ATX markers for headings: rejected because `#` levels are generated editorial structure absent from typewriter text.
- Use bold or italic emphasis: rejected because those Markdown markers are not visible source characters.
- Collapse headings into prose: rejected because a visibly separate heading line remains a meaningful source boundary.

## Decision 5: State artificial letter-spacing normalization with an exact example

**Decision**: Include a prominent prompt rule: collapse artificial typewriter-style spacing between letters anywhere in recognized text while preserving word boundaries, with the canonical example `N A T O   S E C R E T` → `NATO SECRET`.

**Rationale**: A concrete example communicates both operations: single spaces between characters disappear, while the wider gap between words becomes one normal word boundary. The rule is deliberately content-agnostic and applies to headings, labels, table cells, and generic prose. The instruction is semantic rather than a blind replacement, allowing the model to distinguish artificial spacing from genuine standalone tokens.

**Alternatives considered**:

- Remove every space between single-character tokens after OCR: rejected because it would corrupt initials, enumerations, formulas, and genuine isolated symbols.
- Rely on generic "normalize whitespace" wording: rejected because it does not clearly cover the observed typewriter-like output.
- Add a regex postprocessor: rejected because text alone cannot reliably resolve ambiguous single-letter sequences or preserve intended word boundaries.

## Decision 6: Use Ollama's precise named reasoning type and verified lower bound

**Decision**: Type profile reasoning as `bool | Literal["low", "medium", "high"] | None`, set the new Qwen 3.8 profile to `"high"`, preserve standard and FireRed as `None` so the request omits the field, and retain GLM's explicit `False`. Require Ollama Python 0.6.1 or newer, the installed version verified to accept the named levels.

**Rationale**: The installed Ollama 0.6.1 `Client.chat` signature accepts exactly those values. A precise literal union catches invalid strings statically and aligns the local profile with the client contract. A dependency lower bound prevents a fresh environment from resolving an older client that lacks named reasoning levels.

**Alternatives considered**:

- Use `bool | str | None` from the starting diff: rejected because arbitrary strings would pass local type checking even though the client rejects them.
- Set high reasoning on standard or every mode: rejected because existing mode request shapes must remain unchanged, GLM deliberately disables reasoning, and standard and FireRed currently omit the field.
- Leave the dependency unconstrained: rejected because named reasoning support would then be environment-dependent.

## Decision 7: Enforce formatting through the model contract, not output rewriting

**Decision**: Make pure Markdown, single-line prose, table fallback, and de-spaced lettering mandatory in the prompt and validate the outgoing request deterministically. Do not add a heuristic formatter to rewrite model output.

**Rationale**: Postprocessing cannot safely tell prose line wraps from list items, table rows, code, fixed-width content, or genuine sequences of standalone letters. Existing normalization removes known reasoning leakage and shared top-level indentation; it should remain narrowly scoped. Representative live Qwen 3.8 samples provide behavioral validation beyond mocked request tests.

**Alternatives considered**:

- Join all adjacent nonblank lines: rejected because it would collapse Markdown blocks.
- Parse and rewrite all returned Markdown: rejected because it adds a large parser scope and can alter source content.
- Treat prompt compliance as optional: rejected because Markdown and single-line paragraphs are mandatory feature outcomes.

## Decision 8: Preserve existing reasoning cleanup and previous-page safety

**Decision**: Continue extracting only response content and applying the existing final-`</think>` cleanup before text becomes previous-page context or saved Markdown. Enable the existing previous-page context pattern for Qwen 3.8 mode and explicitly tell the model that context must not be copied unless visible on the current page.

**Rationale**: Ollama responses can expose reasoning separately, while observed models may still leak it inline. The existing normalization covers the inline case. A prompt-level context rule reduces accidental repetition while leaving every existing mode unchanged.

**Alternatives considered**:

- Disable previous-page context for Qwen 3.8: rejected because the experimental prompt builds on standard-mode continuity behavior and multipage OCR benefits from context.
- Save the raw content when named reasoning is enabled: rejected because reasoning leakage has already been observed.
- Change GLM or FireRed context behavior: rejected because specialized modes are outside this feature.

## Decision 9: Test exact Qwen 3.8 requests and existing-mode isolation

**Decision**: Add exact Qwen 3.8 profile and request tests for its prompts, previous-page context, and `think="high"`; verify retries reuse the identical request; assert the selected model identifier passes through unchanged; and retain exact standard omission, GLM `think=False`, and FireRed omission assertions. Prompt-contract tests explicitly cover the prohibition on generated heading/bold/italic markers and artificial spacing in headings, prose, labels, and table cells.

**Rationale**: Prompt-driven behavior is best protected by exact request-contract tests. Separate assertions for all four modes prevent the new resolver value and shared reasoning type from altering existing requests. Mocked tests remain deterministic, while the quickstart defines representative live review for plain typewriter headings, Markdown-compatible structure, prose joining, and typewriter spacing anywhere in text.

**Alternatives considered**:

- Test only prompt substrings: rejected because removed or contradictory rules could return unnoticed.
- Test only live model output: rejected because model output is nondeterministic and requires external service state.
- Snapshot every unrelated OCR workflow: rejected because existing focused regression tests already cover those contracts.

## Decision 10: Prohibit inferred curly braces in typewritten source

**Decision**: State in the Qwen 3.8 prompt that the target typewriters did not provide curly braces. Never infer or normalize a source character into `{` or `}`; output a curly brace only when it is unambiguously visible in the current image.

**Rationale**: A vision model can normalize an ambiguous typewritten glyph into a modern character that was unavailable on the source machine. The explicit negative rule protects documentary fidelity while the visibility exception preserves genuinely printed, stamped, handwritten, or otherwise present braces.

**Alternatives considered**:

- Remove every curly brace after OCR: rejected because a brace can be genuinely and unambiguously visible in non-typewritten additions or other source material.
- Rely only on the general no-inference rule: rejected because it does not identify the observed character-normalization failure.
- Add a deterministic brace postprocessor: rejected because output text cannot establish whether a brace was visibly present in the image.
