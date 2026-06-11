# Contract: Generated Document Interlink Targets

## Scope

This contract covers generated Markdown links from one vault document note to another, including metadata references rows, body links, and language-version rows.

## Inputs

- Current document archive code.
- Current document path or filename.
- Interlink code map containing language labels and target paths.
- References row archive codes and body archive-code mentions.
- Example target path:
  - `NPG - Nuclear Planning Group/1 NPG - Nuclear Planning Group/1974/NPG-D(74)12_FRE.md`
  - `NPG - Nuclear Planning Group/3 NPG(STUDY) - Nuclear Planning Study/NPG(STUDY)38_ENG.md`

## Output Behavior

- Generated links use the original visible label.
- The Markdown link destination is the target filename only.
- Example:
  - Expected: `[French](NPG-D(74)12_FRE.md)`
  - Not expected: `[French](NPG - Nuclear Planning Group/1 NPG - Nuclear Planning Group/1974/NPG-D(74)12_FRE.md)`
  - Expected: `[NPG(STUDY)/38](NPG(STUDY)38_ENG.md)`
  - Not expected: `[NPG(STUDY)/38](NPG - Nuclear Planning Group/3 NPG(STUDY) - Nuclear Planning Study/NPG(STUDY)38_ENG.md)`
- Existing language-version row replacement remains idempotent.
- Existing generated reference and body links remain idempotent unless force-updated.
- Unrelated non-generated link types are unchanged by this contract.

## Verification

- Unit tests must cover language-version, references-row, and body-link generation from nested stored target paths.
- Unit tests must assert filename punctuation is preserved.
- Integration or CLI tests must cover generated vault notes where generated document links contain only target filenames.
