# Quickstart Validation Guide: Resume-Safe Metadata and Prompt Isolation

This guide describes how to run and verify the validation scenarios for resume-safe metadata and prompt isolation.

## Prerequisites
- The virtual environment is active.
- Ollama is running locally.

---

## Scenario 1: Resume-Safety and Preflight Scan

Verify that processed files are skipped and tags are not double-counted when running the pipeline again.

### Steps
1. Create a dummy test directory with 3 markdown files.
2. Run `ocrpolish metadata` to process them:
   ```bash
   ocrpolish metadata tests/data/input_dummy tests/data/output_dummy
   ```
3. Observe that all 3 files are processed.
4. Run the command again with `--overwrite false` (or default):
   ```bash
   ocrpolish metadata tests/data/input_dummy tests/data/output_dummy
   ```
5. Check the logs.

### Expected Outcome
- The second run must skip all 3 files in under 2 seconds.
- The global counters parsed from the output directory must be identical to the first run (verified by logging statements or running unit tests).

---

## Scenario 2: Prompt Isolation (Strips Generated Sections)

Verify that when a previously processed file is re-processed, the LLM prompt is isolated from the old generated sections.

### Steps
1. Create an enriched Markdown file in the input directory that already has YAML frontmatter, a `> [!info] Metadata` callout, an `> [!abstract]` callout, and a `> [!citing this document]` callout.
2. Run metadata processing on the file.
3. Inspect the prompt content passed to the LLM (e.g. by enabling debug logging or mocking the LLM client call).

### Expected Outcome
- The prompt sent to the LLM contains only the clean body text.
- The YAML frontmatter, Metadata callout, Abstract callout, and Citing callout are completely stripped and absent from the LLM prompt context.

---

## Scenario 3: Deterministic Citekey Generation

Verify that the `citekey` field is generated correctly from filename stem and path modes.

### Steps
1. Run the metadata command with default options:
   ```bash
   ocrpolish metadata tests/data/input_dummy tests/data/output_dummy
   ```
2. Verify the frontmatter of `tests/data/output_dummy/file.md` has `citekey: file` (normalized).
3. Run the metadata command with path mode:
   ```bash
   ocrpolish metadata tests/data/input_dummy tests/data/output_dummy --citekey-mode path
   ```
4. Verify the frontmatter has `citekey: tests-data-output_dummy-file` (or similar normalized relative path).

### Expected Outcome
- The `citekey` field exists in frontmatter and the metadata table.
- The BibTeX citation block uses this citekey instead of `archive_code`.
