# Implementation Plan: Qwen 3.8 Markdown OCR Profile

**Branch**: `038-qwen38-markdown-prompts` | **Date**: 2026-08-31 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/038-qwen38-markdown-prompts/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Add a dedicated `qwen38` OCR mode with one concise, non-contradictory Markdown transcription contract. The contract mandates correct `#`/`##`/`###` heading hierarchy, pure Markdown, one physical line per prose paragraph, column-one top-level blocks, Markdown-safe table fallback, source fidelity, and normalization of artificial typewriter-style letter spacing anywhere in text with the explicit `N A T O   S E C R E T` → `NATO SECRET` example. Widen the profile's reasoning type to the Ollama client's supported literal levels and send `think="high"` only for the new mode. Preserve standard, GLM, and FireRed request behavior along with the existing model default, response normalization, retries, timing, and output lifecycle.

## Technical Context

**Language/Version**: Python 3.12 (`requires-python = ">=3.12"`)

**Primary Dependencies**: Click CLI, Ollama Python client 0.6.1 or newer, httpx, PyPDF2, pdf2image, Python dataclasses and typing literals

**Storage**: Existing local PDF input and Markdown output; no storage or schema changes

**Testing**: pytest and pytest-cov with mocked Ollama requests/responses, focused request-contract tests, CLI integration tests, and manual representative Qwen 3.8 output review

**Target Platform**: macOS and Linux CLI clients connecting to a local or remote Ollama service with `qwen38` selected through the existing mode option and a Qwen 3.8 model selected through the existing model option

**Project Type**: Single-project command-line application

**Performance Goals**: Add no model calls, renders, retries, or output-processing passes; prompt and request construction remain constant-time relative to page content

**Constraints**: Qwen 3.8 mode output must use supported Markdown heading hierarchy, pure Markdown, unwrapped prose paragraphs, and normalized artificial letter spacing in any text; high reasoning applies only to `qwen38`; prompt enforcement must not introduce a heuristic output rewriter; standard, GLM, FireRed, and the existing OCR lifecycle remain unchanged

**Scale/Scope**: One new mode/profile, two new prompt constants, one reasoning field type, one CLI choice, one dependency lower bound, focused unit/integration assertions, and Feature 038 documentation; existing recursive batches of multipage PDFs remain supported

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. Quality-Driven Python Development — PASS**: The design remains in Python 3.12, uses a precise literal type for reasoning levels, and defines Ruff, Flake8, MyPy, pytest, and coverage validation.
- **II. CLI-First Interface — PASS**: Operators continue to use the existing OCR command and model option; no secondary interface is introduced.
- **III. Recursive Directory Processing — PASS**: Recursive PDF discovery, mirrored output paths, page ordering, and resume behavior are unchanged.
- **IV. Data Isolation — PASS**: Automated validation uses prompt/request assertions and disposable mocked files. Representative archival inputs and live model outputs remain outside version control.
- **V. Atomic Git Workflow — PASS**: Prompt/profile tests, implementation, documentation, and dependency metadata can be committed in scoped logical increments without staging unrelated files.

**Pre-design gate result**: PASS. No constitutional violations or unresolved clarifications.

## Project Structure

### Documentation (this feature)

```text
specs/038-qwen38-markdown-prompts/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── qwen38-ocr-profile.md
└── tasks.md                    # Created later by /speckit-tasks
```

### Source Code (repository root)

```text
archivatorium/
├── cli.py                      # Add qwen38 to the existing mode choice
└── ocr_engine.py               # Qwen 3.8 prompts/profile, reasoning type, mode resolution

tests/
├── unit/
│   └── test_ocr_engine.py      # Exact prompt/profile and mode-isolation contracts
└── integration/
    └── test_ocr_cli.py         # Visible CLI-selected model and request behavior

pyproject.toml                  # Verified Ollama client lower bound for named reasoning levels
```

**Structure Decision**: Add one immutable Qwen 3.8 profile beside the existing standard, GLM, and FireRed profiles; extend the existing mode resolver and Click choice with `qwen38`; and reuse the existing message/request builders to serialize its prompts, previous-page context, options, and `think="high"`. Do not mutate existing profiles or add a postprocessor, model-name branch, service, or storage format.

## Complexity Tracking

No constitutional violations require justification.

## Post-Design Constitution Check

- **I. Quality-Driven Python Development — PASS**: Phase 1 defines exact request and prompt contracts, precise reasoning typing, deterministic regression coverage, and full quality gates.
- **II. CLI-First Interface — PASS**: The contract is selected through the existing OCR command with the new `qwen38` mode value and a Qwen 3.8 model supplied through the existing model option.
- **III. Recursive Directory Processing — PASS**: The design changes request content only and preserves recursive processing and mirrored output.
- **IV. Data Isolation — PASS**: Quickstart automation uses mocks; live samples are operator-provided and remain untracked.
- **V. Atomic Git Workflow — PASS**: All planned files are explicitly scoped and unrelated dirty tests and datasets remain excluded.

**Post-design gate result**: PASS. Phase 1 introduces no constitutional violations.
