# Contract: Tagging Prompt Behavior

## Scope

This contract defines the externally observable behavior of the metadata tagging prompt used by the existing `ocrpolish metadata` flow. It does not add CLI options, output fields, taxonomy files, useful-tags files, tests, parser logic, or post-processing steps.

## Existing Interface

Users continue to invoke metadata extraction through the existing CLI:

```text
ocrpolish metadata INPUT_DIR OUTPUT_DIR --hierarchy-file TAXONOMY_YAML --tags-file USEFUL_TAGS_YAML [existing options]
```

The command continues to emit the same metadata sections and tag categories:

- `#Entities/...`
- `#Topics/...`
- `#Tags/...`

## Prompt Requirements

The tagging prompt must include guidance that is visible in the generated prompt text for each tagging window:

- When available, the full source-relative filename appears before the full document text.
- The filename can be used as contextual evidence for archival code, document year/date, series, collection, or folder-level context when consistent with the full document text.
- Filename context must not override clearly contradictory document text.
- Entity formats remain `State/<name>`, `Org/<name>`, `City/<country>/<city>`, and `Person/<name>`.
- States, organisations, and cities use English canonical names when the intended entity is clear.
- State, city, person, and organisation names use title case, except standard acronyms remain all caps.
- French or alternate forms normalize to the expected English form for known sample patterns, including Brussels/Bruxelles, Germany/Allemagne, United States/USA, and NATO/OTAN.
- Obvious OCR corruption in known entity names is corrected only when context identifies the intended entity.
- Ambiguous damaged strings must not be converted into invented canonical entities.
- Topic-tag reasons continue to require direct quoted evidence from the source text.
- Topic extraction is mandatory and multi-label for substantive archival text: the prompt must tell the model to review the full approved taxonomy, emit all supported Category/Topic entries rather than only the single best topic, and use `topic_tags: []` only when no approved taxonomy topic is clearly supported.
- Conceptual tags continue to prioritize useful/resumed vocabularies and preserve meaningful acronyms.
- Substantive conceptual-tag extraction requires at least 1 conceptual tag, while still allowing every clearly justified useful conceptual tag and imposing no hard maximum.
- Prompt and structured response schema order must be `topic_tags`, then `entity_tags`, then `conceptual_tags`, corresponding to Categories/Topics, Entities, and Tags.
- Conceptual tags must strictly exclude entity duplicates after `entity_tags` are chosen, including exact names, aliases, translated names, acronyms, expanded names, punctuation/case variants, hyphenation variants, and compacted normalized forms for the same organisation, state, city, or person.
- Entity-related conceptual tags are allowed only when they add substantive archival meaning beyond the entity itself.
- Conceptual tags must not include both an abbreviation and expanded full-name form for the same concept; for well-known NATO-domain terms, the standard acronym is preferred.

## Required Example Coverage

The prompt text must cover these expected mappings:

| Source pattern | Expected emitted value |
|----------------|------------------------|
| `nato`, `OTAN`, or a long French NATO name | `Org/NATO` |
| `Bruxelles` | `City/Belgium/Brussels` |
| `Allemagne` | `State/Germany` |
| `USA` or `usa` | `State/United-States` |
| Clear OCR damage in a recurring organisation name | Standard organisation entity form |
| `Collection-Series/1974/ORG-DOCUMENT-1974-05.md` | Prompt includes the full relative filename as context before the full document text |
| An acronym and expanded-name form for the same conceptual tag candidate | One canonical conceptual tag, preferably the standard acronym when the acronym is the accepted domain form |
| `Org/NATO` plus conceptual candidate `NATO` or `NorthAtlanticTreatyOrganization` | Keep the entity; do not emit the duplicate conceptual tag |

## Non-Goals

- No new CLI command or option.
- No generated metadata category-set change; the existing category fields are retained while their prompt/schema declaration order may be adjusted for LLM decoding.
- No migration or cleanup of existing vault output.
- No taxonomy or useful-tags file rewrite.
- No deterministic post-generation canonicalization layer.
- No test-code changes.
- No metadata extraction, parser, schema, output rendering, or post-processing logic changes beyond passing existing filename context into the prompt.
