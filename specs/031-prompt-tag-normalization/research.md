# Research: Prompt Tag Normalization

## Decision: Implement prompt hardening, not a normalization layer

**Rationale**: The feature request explicitly limits the enhancement to LLM prompt text changes. The v6 analysis shows that many failures originate in generated values before downstream normalization, including casing mismatches, multilingual duplicates, OCR-damaged entities, and hierarchy confusion. Prompt instructions can target those generation choices without changing Python logic, schemas, parsers, output files, tests, or stored metadata.

**Alternatives considered**:

- Add post-processing normalization rules: rejected because it violates the LLM-prompt-only boundary and would require a separate mapping/validation surface.
- Modify taxonomy or useful-tags YAML: rejected because the issue is entity generation consistency, not taxonomy structure.
- Migrate existing generated metadata: rejected because the feature is scoped to future generation behavior and validation.
- Add or change automated tests: rejected for this correction because tests are code; validation should use existing test commands, prompt inspection, and optional sample runs unless the scope is explicitly expanded.

## Decision: Use explicit canonicalization guidance with examples

**Rationale**: The analysis report identifies concrete duplicate families: NATO/nato/OTAN, Brussels/Bruxelles, Germany/Allemagne, United States/USA, and OCR-damaged variants of recurring organisation names. A prompt with direct rules plus examples gives the model clear expected outputs while remaining easy to validate through prompt inspection and sample runs.

**Alternatives considered**:

- Add only a short generic "normalize names" rule: rejected because the sample failures are specific and recurring enough to justify concrete examples.
- Add a long exhaustive translation table: rejected for this feature because it would increase prompt size and maintenance burden without evidence that every possible country/city alias needs to be enumerated.

## Decision: Preserve acronym behavior while fixing casing noise

**Rationale**: The existing prompt already requires meaningful all-caps abbreviations to be included and normalizes non-acronym all-caps terms. The new guidance must strengthen entity casing without suppressing valid domain acronyms such as NATO, SHAPE, SACLANT, SACEUR, and DPC.

**Alternatives considered**:

- Force all names into title case: rejected because standard acronyms would be degraded.
- Preserve all source casing: rejected because the sample shows lowercase and shouting-case variants fragment the vocabulary.

## Decision: Make OCR recovery conservative

**Rationale**: The data sample shows clear OCR corruption such as `ST/FF`, `Sta-F`, and `St-1F` becoming one-off entity values. The prompt should ask for correction only when context clearly identifies the intended entity, and should avoid inventing canonical names from ambiguous damaged text.

**Alternatives considered**:

- Always map damaged-looking strings to the closest known entity: rejected because it risks false positives.
- Ignore OCR damage entirely: rejected because the report shows it is a measurable source of vocabulary fragmentation.

## Decision: Validate through prompt inspection, existing regression tests, and representative sample behavior

**Rationale**: The corrected requirement forbids code changes beyond LLM prompt text. Validation should inspect the generated prompt content, run existing regression tests to catch accidental breakage, and use a small representative set of excerpts to check expected generated tags when an LLM-backed validation run is available.

**Alternatives considered**:

- Require a full corpus re-run for completion: rejected because it is slow, model-dependent, and not necessary to verify the prompt contract.
- Add new prompt unit tests: rejected because modifying tests is still code work and is outside the corrected scope.
- Test only by reading the prompt manually: rejected as the sole approach because existing regression commands and optional sample runs provide stronger validation without changing code.
