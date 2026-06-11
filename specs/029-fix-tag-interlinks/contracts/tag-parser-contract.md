# Contract: Generated Entity Tag Parsing

## Scope

This contract covers generated `#Entities/Org/...` and `#Entities/State/...` tags discovered in Markdown text.

## Inputs

- Markdown text containing generated canonical tags.
- Relevant tag examples:
  - `#Entities/Org/OTAN/NATO`
  - `#Entities/Org/NAC/DP`
  - `#Entities/Org/Council/DPC`
  - `#Entities/State/USA/California`

## Output Behavior

- `#Entities/Org/OTAN/NATO` is accepted as `Entities/Org/OTAN-NATO`.
- `#Entities/Org/NAC/DP` is accepted as `Entities/Org/NAC-DP`.
- `#Entities/Org/Council/DPC` is accepted as `Entities/Org/Council-DPC`.
- `#Entities/State/USA/California` is accepted as `Entities/State/USA-California`.
- Accepted organization and state values are available in the existing canonical tag collections using their normalized lowercase values.
- No malformed-generated-tag warning is emitted when the slash-containing name is the only invalid condition.

## Non-Goals

- Do not flatten hierarchical topic or conceptual tags.
- Do not change city tag structure.
- Do not accept unsupported entity types.
- Do not suppress warnings for tags that remain malformed after normalization.

## Verification

- Unit tests must assert raw paths and entity collections for the reported examples.
- Warning-capture tests must assert that the reported examples do not log malformed-tag warnings.
- Existing malformed-tag tests must continue to pass.
