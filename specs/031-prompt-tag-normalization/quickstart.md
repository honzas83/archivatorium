# Quickstart: Validate Prompt Tag Normalization

## Prerequisites

- Python 3.12 environment with project dependencies installed.
- Existing taxonomy and useful-tags YAML fixtures or real project files.
- Access to representative excerpts based on `COUNTS_v6.csv` and `docs/tag_analysis_report.md`.

## 1. Inspect the prompt contract

Review [contracts/tagging-prompt-contract.md](./contracts/tagging-prompt-contract.md) and confirm the implementation remains LLM-prompt-text-only.

Expected outcome:

- No CLI options, schemas, taxonomy files, useful-tags files, tests, parsers, or post-processing code are required by the design.

## 2. Inspect the generated prompt text

Inspect the prompt string produced for tagging and confirm it includes the contract items.

Expected outcome:

- Prompt text includes entity normalization, English canonicalization, OCR recovery, acronym preservation, and required examples.
- Prompt text includes the full source-relative filename when available and describes it as contextual information for archival code, year/date, series, or collection context.
- Prompt text and structured schema present categories in order: `topic_tags`, then `entity_tags`, then `conceptual_tags`.
- Prompt text and structured schema descriptions make topic extraction mandatory and multi-label for substantive archival text, asking for all supported approved taxonomy topics and allowing `topic_tags: []` only when no approved taxonomy topic is clearly supported.
- Prompt text and structured schema require at least 1 conceptual tag for substantive documents and impose no hard maximum.
- Prompt text instructs the model to strictly exclude entity duplicates from conceptual tags after `entity_tags` are chosen, including aliases, acronyms, translations, expanded names, punctuation/case variants, hyphenation variants, and compacted forms.
- Prompt text instructs the model not to emit both abbreviation and expanded full-name conceptual tags for the same concept, preferring standard domain acronyms when they are the accepted canonical form.
- No non-prompt code changes are needed to validate this step.

## 3. Run existing prompt regression tests

```bash
pytest tests/unit/test_tagging_service.py
```

Expected outcome:

- Existing prompt behavior remains intact.
- No test files are modified for this feature.

## 4. Run metadata command regression tests

```bash
pytest tests/integration/test_metadata_command.py
```

Expected outcome:

- The `ocrpolish metadata` command still requires the same taxonomy and useful-tags inputs.
- No new options or output contract changes are introduced.

## 5. Run the standard quality gates

```bash
ruff check .
ruff format --check .
flake8
mypy .
pytest
```

Expected outcome:

- The prompt-only change passes the repository quality gates required by the constitution.

## 6. Optional LLM-backed sample validation

Run metadata extraction on a small validation folder containing excerpts with these patterns:

- `nato`, `OTAN`, and a long French NATO name.
- `Bruxelles` and `Allemagne`.
- `USA` and `usa`.
- Clear OCR-damaged variants of recurring organisation names.
- A nested relative filename containing archival code, folder context, and year/date.
- A non-acronym all-caps term and meaningful acronyms such as NATO, SHAPE, SACLANT, SACEUR, or DPC.
- An acronym/full-name pair for the same concept.
- An entity/concept duplicate pair, such as `Org/NATO` plus conceptual candidates `NATO` or `NorthAtlanticTreatyOrganization`.

Expected outcome:

- Clear variants converge to the canonical values listed in the contract.
- Ambiguous OCR damage does not create invented entities.
- Topic reasons still include direct source-text evidence.
- Rare but justified substantive concepts remain eligible as conceptual tags.
- Filename context informs metadata only when it is consistent with the full document text.
- Entity names and aliases are not repeated as conceptual tags unless the conceptual tag adds distinct substantive archival meaning.
- Clear acronym/full-name conceptual duplicates collapse to one canonical tag.
