# Phase 0 Research: Normalize Qwen 3.8 OCR Output

## Decision 1: Normalize at the successful model-response boundary

**Decision**: Apply one model-independent normalization function to successful text inside `OCREngine.ocr_single_page`, after extracting response content and before logging its final length or returning it to `run_ocr`.

**Rationale**: This boundary covers direct page recognition, normal multipage runs, resumed runs, retries, and every OCR mode without duplicating logic. The normalized text then becomes both saved page content and any previous-page context, preventing leaked reasoning or artificial indentation from propagating.

**Alternatives considered**:

- Normalize only while assembling Markdown: rejected because direct callers and previous-page context would still receive raw model output.
- Enable cleanup only when the model name contains `qwen3.8`: rejected because model identifiers are user-controlled and the cleanup rules are safe and required for every supported response.
- Add a Qwen-specific OCR mode: rejected because request construction is unchanged and the issue concerns response sanitation.

## Decision 2: Use the final exact closing marker as the reasoning boundary

**Decision**: Search for the final exact, case-sensitive `</think>` marker. If found, discard the marker and every preceding character, then remove blank separator lines before the remaining OCR content. If absent, do not remove a reasoning prefix.

**Rationale**: The observed marker is the only reliable boundary supplied by the model. Selecting the final occurrence prevents an earlier marker embedded in leaked reasoning from leaving additional non-document text. Exact matching avoids deleting legitimate text with merely similar spelling.

**Alternatives considered**:

- Use the first closing marker: rejected because later reasoning fragments could remain.
- Require a matching opening `<think>` marker: rejected because the observed failure only guarantees the closing marker.
- Remove text matching broad “thinking” patterns: rejected because heuristic deletion could destroy recognized document content.

## Decision 3: Dedent by common leading ASCII spaces only

**Decision**: After marker cleanup, inspect all nonblank lines. If every nonblank line begins with one or more ASCII spaces and no indentation prefix contains a tab, remove the smallest leading-space count from every nonblank line. Ignore and preserve blank lines when calculating or removing indentation.

**Rationale**: This exactly handles the observed four/eight-space case: four shared spaces are removed while four spaces of relative nesting remain. An unindented line naturally produces a zero minimum and prevents any change. Preserving tab-containing indentation avoids ambiguous visual-width conversions.

**Alternatives considered**:

- Strip all leading whitespace from every line: rejected because it destroys lists, nested blocks, and fixed-width structure.
- Use the first line's indentation: rejected because the first line may be more deeply nested than later lines.
- Use general-purpose dedenting or expand tabs: rejected because those rules can alter mixed indentation without a defined tab width.

## Decision 4: Measure one complete per-PDF run with a monotonic clock

**Decision**: Start a monotonic timer on entry to `run_ocr` and stop it in a `finally` path. Count a page once when it is not resumably skipped and is about to enter rendering. Log attempted-page count, total elapsed seconds, and total divided by attempted pages; log an explicit unavailable average when the count is zero.

**Rationale**: One `run_ocr` call is the existing lifecycle for one input PDF. Whole-invocation timing includes page counting, resume parsing, rendering, remote requests, retry waits, cleanup, merging, output writes, and failure time. A monotonic clock is immune to wall-clock adjustments. The `finally` path preserves visibility when a page fails and the CLI continues to the next PDF.

**Alternatives considered**:

- Sum individual successful request durations: rejected because it excludes rendering, retry waits, failures, and output work.
- Divide by total PDF page count: rejected because resumed pages are skipped and incur no OCR attempt.
- Replace per-PDF summaries with only an outer CLI aggregate: rejected because per-document summaries identify slow or failed PDFs. The command-wide aggregate is emitted in addition to them.

## Decision 5: Keep the log stable and machine-readable

**Decision**: Emit one INFO summary per `run_ocr` invocation using explicit fields: `attempted_pages`, `total_seconds`, and `average_seconds_per_page`. Also emit one command-wide INFO summary using `overall_attempted_pages`, `overall_total_seconds`, and `overall_average_seconds_per_page`. Start the outer monotonic clock on entry to the OCR command, sum each run's distinct attempted-page count, render seconds to three decimal places, and use `unavailable` for either zero-page case.

**Rationale**: Named fields are readable in normal CLI output, easy to assert in tests, and suitable for later log parsing. Keeping separate field prefixes prevents a per-PDF summary from being mistaken for the whole batch. The command timer includes initialization, discovery, all document runs, handled failures, writes, and CLI overhead.

**Alternatives considered**:

- Report pages per second only: rejected because the requested measure is average time for one page.
- Log one timing line per page: rejected because it adds noise and does not directly provide run throughput.
- Add a new CLI output-format option: rejected because existing logging is sufficient.

## Decision 7: Expose command-wide throughput during long batches

**Decision**: After every PDF run, emit a cumulative INFO line with `attempted_pages_since_command_start`, `elapsed_seconds_since_command_start`, and `average_seconds_per_page_since_command_start`. Retain the final overall summary.

**Rationale**: A final-only command summary is invisible while a long batch is still running. Updating the cumulative snapshot at the existing per-PDF boundary makes current whole-command throughput observable without adding page-level noise or changing OCR execution.

**Alternatives considered**:

- Emit only at command completion: rejected because operators cannot monitor an active long-running batch.
- Emit after every input page: rejected because it requires a new engine-to-CLI callback and would add substantial log noise.
- Replace the per-PDF summary: rejected because document-level and command-level performance answer different operational questions.

## Decision 6: Preserve existing OCR contracts

**Decision**: Do not change model defaults, mode profiles, prompts, request options, retries, recursive discovery, output names, page ordering, resume semantics, or the `run_ocr` return type.

**Rationale**: The requested adaptation concerns returned text and observability. Keeping the existing request and output lifecycle limits regression risk and lets Qwen, GLM, FireRed, and custom-model workflows benefit equally.

**Alternatives considered**:

- Make Qwen 3.8 the default model: rejected because it is selected through the existing `--model` option and no default change was requested.
- Return a new result object containing metrics: rejected because it would broaden the public engine contract solely for a log-side requirement.
