# Data Model: Normalize Qwen 3.8 OCR Output

This feature adds transient text and run measurements. It does not introduce a database, configuration file, or Markdown metadata change.

## Raw OCR Response

Text returned by one successful model request before application cleanup.

| Field | Type | Validation | Meaning |
|-------|------|------------|---------|
| `content` | string | May be empty; may contain any number of exact `</think>` markers | Model-provided response for one rendered page. |

## Normalized Page Text

Text returned to the OCR pipeline after deterministic cleanup.

| Field | Type | Validation | Meaning |
|-------|------|------------|---------|
| `content` | string | Contains only content after the final marker when present | Candidate transcription for the page. |
| `shared_indent` | non-negative integer | Minimum leading ASCII-space count across nonblank lines, or zero | Number of top-level spaces removed from each nonblank line. |

### Normalization state transition

1. `response-received`
2. `reasoning-boundary-checked`
3. If a marker exists: `prefix-discarded -> leading-blank-separators-removed`
4. `nonblank-lines-inspected`
5. If indentation is safe and shared: `common-indent-removed`
6. `normalized`

### Invariants

- Only the final exact `</think>` marker creates a prefix boundary.
- No-marker input retains all content except any independent common-indent normalization.
- Relative indentation differences between nonblank lines remain unchanged.
- An unindented nonblank line, a tab-indented line, or mixed tab/space indentation results in `shared_indent = 0`.
- Whitespace-only lines do not affect `shared_indent` and remain unchanged.

## OCR Run Metrics

Measurements for one `run_ocr` invocation, corresponding to one input PDF.

| Field | Type | Validation | Meaning |
|-------|------|------------|---------|
| `attempted_pages` | non-negative integer | Incremented once for each non-skipped page before rendering | Distinct input pages for which OCR work was attempted. |
| `total_seconds` | non-negative number | Monotonic end time minus start time | Full invocation time, including page counting, resume parsing, rendering, requests, retries, cleanup, merging, writes, and failures. |
| `average_seconds_per_page` | optional non-negative number | `total_seconds / attempted_pages` when count is positive; otherwise unavailable | Effective average time for one attempted input page. |

### Page contribution rules

| Page state | Counted as attempted | Time represented |
|------------|----------------------|------------------|
| Existing non-empty page skipped during resume | No | Its discovery and resume-parsing overhead remains in total time. |
| Page rendered and recognized successfully | Yes, once | Rendering, request, cleanup, merge, and write time. |
| Page retried before success | Yes, once | All request attempts and retry waits. |
| Page fails and aborts its document run | Yes, once | Work through the failure; summary still logs from `finally`. |
| PDF with zero pages or all pages skipped | No | Average is unavailable. |

## OCR Command Metrics

Measurements for one invocation of the `ocr` CLI command, potentially spanning multiple PDFs.

| Field | Type | Validation | Meaning |
|-------|------|------------|---------|
| `overall_attempted_pages` | non-negative integer | Sum of `attempted_pages` from every invoked per-PDF run | Distinct non-skipped pages attempted across the command. |
| `overall_total_seconds` | non-negative number | Monotonic command end time minus command-entry time | Engine setup, recursive discovery, all PDF runs, handled failures, writes, and CLI overhead. |
| `overall_average_seconds_per_page` | optional non-negative number | `overall_total_seconds / overall_attempted_pages` when positive; otherwise unavailable | Effective whole-command average time for one attempted input page. |

## Relationships

- One input PDF creates one OCR run and one timing summary.
- One OCR command creates one command-wide timing summary and may contain zero or more per-PDF runs.
- Each per-PDF run contributes its distinct attempted-page count once to `overall_attempted_pages`, including runs that end in handled failure.
- One attempted page may make multiple model requests because of retries but contributes one unit to `attempted_pages`.
- One successful model response creates one normalized page text value.
- Normalized page text feeds saved Markdown and, only for modes that permit it, subsequent-page context.
