# Research: NATO Topic Taxonomy V2

## Decision: Preserve the two-level taxonomy and add versioned root metadata

**Decision**: Keep `categories -> category -> topics -> topic` and add `schema_version: 2`, a root
`classification_policy`.

**Rationale**: All current consumers understand two-part `Category/Topic` paths, and the indexing
service ignores unrelated root keys. Root policy metadata makes the universal rule machine-checkable
without broadening the output contract.

**Alternatives considered**:

- Add a third hierarchy level: rejected because parsing, prompts, outputs, indexes, and archive links
  consistently assume two components.
- Put the universal rule in every topic: rejected because duplication invites inconsistent edits.

## Decision: Use six categories and 55 topics

**Decision**: Organize the taxonomy as follows:

- Nuclear Doctrine and Deterrence: 6 topics.
- Nuclear Planning, Deployment, and Control: 7 topics.
- Alliance Governance and Institutions: 9 topics.
- Treaties and Arms Control: 7 topics.
- Military Operations and Capabilities: 13 topics.
- Geopolitics and Crises: 13 topics.

The 53 v1 topics are retained except that two overloaded topics are each replaced by two narrower
topics, yielding 55. Article 5 moves to governance; Civil Emergency Planning moves to operations;
nuclear planning/policy topics move into the new nuclear-planning category.

**Rationale**: The placement separates doctrine from operational control, alliance governance from
capabilities, and organizational structure from shared physical infrastructure while preserving the
existing output depth.

**Alternatives considered**:

- Put Civil Emergency Planning under governance: rejected because its defining subjects are
  operational resilience, continuity, civil defence, and stockpiling.
- Move Energy Security into geopolitics: rejected because that move is not required by the reviewed
  failure patterns and would create unnecessary path churn.

## Decision: Keep explicit taxonomy file selection

**Decision**: Use the existing required `--hierarchy-file` option. Document commands for both v1 and
v2; add no version flag and change no default.

**Rationale**: The current CLI already provides unambiguous opt-in selection and recursively applies
the selected hierarchy. A second selection mechanism could disagree with the file path.

**Alternatives considered**:

- Add `--taxonomy-version`: rejected as redundant and potentially ambiguous.
- Make v2 the default: rejected because it would change existing workflows and archive output.

## Decision: Adopt v2 through a fresh metadata run

**Decision**: Do not design or implement a v1-to-v2 path migration. A maintainer adopts v2 by running
the existing metadata command again with `topics/NATO_themes_v2.yaml`, normally into a separate
output directory.

**Rationale**: Reclassification evaluates each document under the narrower v2 definitions and avoids
guessing whether an old combined assignment maps to neither, either, or both replacement topics.

**Alternatives considered**:

- Add a machine-readable path map: rejected as unnecessary for the requested rerun workflow.
- Rewrite old topic paths: rejected because renamed and split concepts are not semantically
  equivalent and existing archives must remain reproducible.

## Decision: Validate taxonomy data before classification

**Decision**: Add basic structural, type, content, normalized-path, and collision validation for all
taxonomies. For schema v2, additionally require the exact category set and all three policy rules.
Raise a dedicated
validation error instead of silently returning an empty hierarchy.

**Rationale**: An empty or incomplete approved-topic set can look like a successful conservative
classification. Early failure is observable and prevents misleading output.

**Alternatives considered**:

- Validate only v2: rejected because malformed legacy taxonomies would remain silent.
- Validate only when rendering the prompt: rejected because errors would occur later and with less
  useful context.

## Decision: Flatten complete classification context

**Decision**: Retain the topic `description` key and add `category` and `category_description` to each
flat item. Preserve every positive and negative sample. Send an object containing the effective
policy and topic list to the classifier.

**Rationale**: This is additive for existing internal consumers and supplies the category distinctions
currently lost by flattening. Editorial fields such as `new_addition` are not classification context.

**Alternatives considered**:

- Add a redundant `topic` field: rejected because `id` is the only selectable path and extra labels
  can encourage incomplete output.

## Decision: Apply the substantive-subject rule universally

**Decision**: Put the detailed rule in v2 YAML and inject an equivalent built-in policy for valid v1
taxonomies. Align the main prompt, critical output rules, and Pydantic field descriptions: include all
substantively supported topics, prefer omission to marginal matches, accept an empty list, and treat
mentions/entities/citations/administrative form as insufficient.

**Rationale**: The false-positive pattern arises from selection behavior, not only individual topic
definitions. Applying the rule to legacy selection also prevents the service from becoming more
permissive when v1 is explicitly used.

**Alternatives considered**:

- Apply the rule only to v2: rejected because service-level correctness should not depend on a
  taxonomy omitting a safety policy.
- Ask for every “clearly justified” topic: rejected because the current expansive wording encourages
  marginal coverage.

## Decision: Keep real validation material local

**Decision**: Put the reviewed corpus, expected labels, and generated score reports under
`data/039-nato-taxonomy-v2/`. Commit only synthetic test fixtures and test strings.

**Rationale**: This obeys the data-isolation constitution and avoids leaking or bloating the
repository while still enabling the measurable success checks.

**Alternatives considered**:

- Commit XLSX feedback or extracted archive documents: rejected by the constitution.
- Test only synthetic data: rejected because the numeric false-positive and recall goals require the
  reviewed corpus.
