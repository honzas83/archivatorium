# Contract: Conceptual Tag Control and Evolution

## Input vocabulary

- `USEFUL_TAGS.yaml` is a seed vocabulary, not an allowlist.
- Preferred runtime vocabulary contains non-seed tags observed in at least two independent archive
  documents.
- A model may propose a genuinely distinct tag absent from both sources.

## Model request

The existing structured tagging call continues to request:

```text
conceptual_tags: list[str]
```

The prompt requires descending importance and normally 5–12 principal concepts for substantive
documents, while permitting fewer or zero when justified. It forbids entity names, passing-mention
tags, speculative combinations, redundant synonyms, and automatic broader/narrower variants.

No provenance, evidence phrase, justification, rejected alternative, or novelty field is requested.

## Application acceptance

For the whole document, the application:

- normalizes candidate paths;
- removes low-value values and entity/topic collisions;
- removes exact normalized duplicates while retaining the first canonical form;
- retains at most five candidates novel to the document's vocabulary snapshot;
- retains at most 20 candidates total;
- preserves candidate importance order after removals.

Seed or established status never exempts an entity collision. Limits apply after aggregating every
window, not as separate final quotas per window.

## Evolution lifecycle

```text
seed ------------------------------> preferred for inference

first valid non-seed occurrence ---> retained in source document
                                  \-> not preferred for later inference

second independent occurrence ----> established
established ------------------------> preferred for later inference
```

Repeated occurrences or windows within one document count once. Existing archive documents
participate through the normal preflight scan. No registry, migration, demotion, or automatic rewrite
is part of this contract.

## Output

The Markdown contract remains a flat sequence of canonical conceptual tags:

```markdown
## Tags
#Tags/Nuclear-Consultation #Tags/Crisis-Management
```

No lifecycle state is serialized.
