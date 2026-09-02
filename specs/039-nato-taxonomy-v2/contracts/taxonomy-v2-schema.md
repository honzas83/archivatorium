# Contract: NATO Taxonomy V2 YAML

## Root shape

```yaml
schema_version: 2
classification_policy:
  substantive_subject_rule: <non-empty string>
  omission_rule: <non-empty string>
  insufficient_evidence_rule: <non-empty string>
categories:
  - category: <category name>
    description: <non-empty classification context>
    topics:
      - topic: <topic name>
        description: <non-empty substantive definition>
        positive_samples: |
          <one or more non-empty examples>
        negative_samples: |
          <one or more non-empty counterexamples>
```

## Required categories and counts

| Category | Topics |
|---|---:|
| Nuclear Doctrine and Deterrence | 6 |
| Nuclear Planning, Deployment, and Control | 7 |
| Alliance Governance and Institutions | 9 |
| Treaties and Arms Control | 7 |
| Military Operations and Capabilities | 13 |
| Geopolitics and Crises | 13 |
| **Total** | **55** |

Names are normalized only when canonical IDs are derived. Category definitions must occur exactly
once and canonical topic IDs must be unique.

## Validation contract

Loading fails before classification if:

- the root, categories, or topics have the wrong type;
- any required name, description, policy rule, or sample block is empty;
- a category/topic name contains `/` or normalizes to an empty component;
- positive or negative samples are not multiline strings or yield no example;
- normalized paths collide;
- v2 does not contain exactly the required six categories and 55 paths.

Legacy taxonomies may omit v2 root fields but remain subject to basic shape, content, path, and
collision validation.

## Flattening contract

Every output element has:

```yaml
id: <canonical Category/Topic>
category: <canonical category component>
category_description: <complete category description>
description: <complete topic description>
positive_samples:
  - <all non-empty positive lines, in source order>
negative_samples:
  - <all non-empty negative lines, in source order>
```

The prompt payload contains the effective `classification_policy` and `topics` list. Editorial flags
are not classifier inputs.

## Version transition

The v2 YAML contains no path-migration map. Renamed, moved, and split topics are applied by rerunning
metadata extraction against source documents with v2 explicitly selected. The service does not
rewrite existing v1 topic paths.
