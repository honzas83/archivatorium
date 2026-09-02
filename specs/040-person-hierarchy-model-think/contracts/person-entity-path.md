# Contract: Person Entity Paths

## Generated path grammar

```text
relative-person-path = "Person/" surname [ "/" given-identity ]
archive-person-path  = "Entities/" relative-person-path
```

- `surname` is mandatory and non-empty after canonical tag normalization.
- `given-identity` is optional and contains either complete given name(s) or compacted initials.
- No fourth identity component is allowed.
- Titles, ranks, offices, and role modifiers are not identity components.

## Canonical examples

| Mention/context | Generated path |
|-----------------|----------------|
| K-W Andrae | `Entities/Person/Andrae/KW` |
| K. W. Andrae | `Entities/Person/Andrae/KW` |
| Joseph Luns | `Entities/Person/Luns/Joseph` |
| Andrae with no known given name | `Entities/Person/Andrae` |
| Minister Andrae | `Entities/Person/Andrae` |

## Rejected generated candidates

- Missing or empty surname.
- More than surname plus one optional given-identity component.
- A component consisting of a title, office, rank, or role modifier.
- A surname that cannot be recovered from the source without guessing.

Rejected candidates are omitted with an actionable warning; extraction continues for other tags.

## Parser and consumer contract

- The Markdown parser accepts both archive path forms from the grammar.
- Parsed counter/reuse values are `surname` or `surname/given-identity`, normalized to lowercase in
  the existing counter representation.
- `raw_paths` preserves the complete normalized path with canonical entity-type casing.
- Entity sections and XLSX export retain the full `raw_paths` value.
- The People index sorts and groups on the surname component and keeps full paths distinct.
- Parsing and indexing never rewrite the source Markdown.

## Compatibility boundary

Existing combined Person paths remain unchanged in existing files. Because surname-only paths are
valid, a parser cannot safely distinguish a legacy combined component from a true surname. The only
supported adoption path is fresh metadata generation or an explicit user rerun.
