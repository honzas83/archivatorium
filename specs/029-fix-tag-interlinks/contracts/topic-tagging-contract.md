# Contract: Topic Assignment and Counter Context

## Scope

This contract covers generated taxonomy topic assignments and resume-derived topic counter hints used during metadata tagging.

## Inputs

- Source document text.
- Approved taxonomy hierarchy.
- Resume-derived topic counter entries from previously processed eligible generated documents.
- Example counter population:
  - 120 entries ordered by descending frequency.

## Output Behavior

- The tagging instructions and structured metadata descriptions do not impose a hard maximum on `topic_tags`.
- Every clearly justified taxonomy topic may be returned.
- Topic assignments remain constrained to the approved taxonomy.
- Resume-derived topic counter context includes:
  - exactly the top 100 topic counter items when at least 100 entries exist;
  - every available topic counter item when fewer than 100 entries exist.
- Topic counter context remains a hint source and must not authorize topics absent from the approved taxonomy.

## Non-Goals

- Do not make topic counter hints override taxonomy validation.
- Do not merge topic counters into conceptual tag or entity hint sections.
- Do not make prompt context unbounded.

## Verification

- Unit tests must prove reuse-hint construction returns 100 preferred topics from a larger counter.
- Prompt or schema tests must prove topic assignment instructions no longer contain a hard topic maximum.
- Integration tests should cover a dense document fixture with more than 10 justified taxonomy topics when practical.
