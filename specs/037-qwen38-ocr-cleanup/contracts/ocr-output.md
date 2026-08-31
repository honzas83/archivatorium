# OCR Output and Logging Contract

## Command compatibility

```text
archivatorium ocr [OPTIONS] INPUT_DIR OUTPUT_DIR
```

No positional argument, option, default model, mode, or exit behavior changes. Qwen 3.8 continues to be selected through the existing `--model` option. Cleanup applies equally to standard, GLM, FireRed, and custom model selections.

## Page-response normalization

For every successful model response, the engine applies these rules in order before the page is used as context or written to Markdown:

1. Locate the final exact, case-sensitive `</think>` marker.
2. If present, discard every character through and including that marker.
3. Remove leading blank separator lines from the remaining content.
4. Inspect leading ASCII spaces on all nonblank lines.
5. If any nonblank line is unindented or has a tab in its indentation prefix, do not dedent the response.
6. Otherwise, remove the smallest leading-space count from every nonblank line.
7. Preserve blank lines, all remaining relative indentation, and page content.

Example input:

```text
internal reasoning
</think>

    Heading
        Nested item
    Closing line
```

Normalized page text:

```text
Heading
    Nested item
Closing line
```

If no marker is present, prefix removal changes nothing, but indentation normalization still applies.

## Timing log

One summary is emitted at INFO level for each input PDF processed by `run_ocr`, including runs that terminate because a page fails.

For a positive attempted-page count, the stable field contract is:

```text
OCR timing: attempted_pages=10 total_seconds=50.000 average_seconds_per_page=5.000
```

For zero attempted pages:

```text
OCR timing: attempted_pages=0 total_seconds=0.000 average_seconds_per_page=unavailable
```

`total_seconds` is monotonic elapsed time across the complete `run_ocr` invocation. `attempted_pages` counts each non-skipped page once regardless of retries. The displayed average equals total seconds divided by attempted pages and uses the same three-decimal precision.

After all PDFs have been processed, the command emits a second INFO summary:

```text
OCR overall timing: overall_attempted_pages=24 overall_total_seconds=132.000 overall_average_seconds_per_page=5.500
```

For a command that attempts no pages, including an input directory with no PDFs:

```text
OCR overall timing: overall_attempted_pages=0 overall_total_seconds=0.250 overall_average_seconds_per_page=unavailable
```

`overall_total_seconds` starts when the OCR command function is entered and includes engine initialization, recursive discovery, all per-PDF work, handled failures, writes, and CLI overhead. `overall_attempted_pages` is the sum of distinct non-skipped pages attempted by every per-PDF run. The overall average equals command-wide total seconds divided by that sum and is rendered to three decimal places.

## Compatibility guarantees

- Existing recognized pages remain skipped during resume and are not counted as attempted.
- Retry count and backoff behavior remain unchanged.
- Saved page ordering, headers, filenames, and directory mirroring remain unchanged.
- Cleanup introduces no additional rendering or model calls.
- The engine's existing text return contract remains unchanged.
