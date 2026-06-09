# CLI Interface Contract: metadata command options

This document defines the CLI arguments and options interface contract for the metadata processing command.

## 1. Metadata Command Options

The `ocrpolish metadata` command accepts the following options:

```bash
ocrpolish metadata <input_dir> <output_dir> [OPTIONS]
```

### Options Specification
- `--citekey-mode [stem|path]`:
  - **Type**: String choice.
  - **Allowed Values**: `stem` (default), `path`.
  - **Description**: Defines the deterministic source used to generate the BibTeX `citekey` field.
    - `stem`: Generates the key from the output filename stem (excluding `.md`).
    - `path`: Generates the key from the vault-relative output path (excluding `.md`).
  - **Default**: `stem`.

---

## 2. Citekey Normalization Specification

Regardless of `--citekey-mode`, the system must normalize the key using a safe character regex.

### Normalization Logic
- Allowed characters: `a-zA-Z0-9\-_:`
- Slashes `/` in path mode must be converted to colons `:` (e.g. `folder/subfolder/file` becomes `folder:subfolder:file`).
- Replace all other invalid characters with a hyphen `-`.
- Collapse multiple hyphens into a single hyphen and strip leading/trailing hyphens.

### Examples
| Input | Mode | Expected Normalized Citekey |
|---|---|---|
| `NPG/D(74)2.md` | `stem` | `NPG-D-74-2` |
| `sub/folder/NPG/D(74)2.md` | `path` | `sub:folder:NPG-D-74-2` |

---

## 3. Metadata Table Output Contract

The rendered metadata table in the output Markdown file matches the canonical model.
Derived navigation fields (such as interlinking-derived references or language versions) must be labeled explicitly with `(derived)` or a similar suffix, and must not modify the YAML frontmatter.

### Table Field Labels
- `title` -> `≡&nbsp;**title**:`
- `summary` -> `≡&nbsp;summary:`
- `pages` -> `№&nbsp;**pages**:`
- `source` -> `🔗&nbsp;source:`
- `sender` -> `≡&nbsp;sender:`
- `recipient` -> `≡&nbsp;recipient:`
- `intent` -> `≡&nbsp;intent:`
- `author_name` -> `≡&nbsp;author_name:`
- `author_institution` -> `≡&nbsp;author_institution:`
- `date` -> `🗓&nbsp;**date**:`
- `archive_code` -> `≡&nbsp;archive_code:`
- `citekey` -> `≡&nbsp;citekey:`
- `language` -> `≡&nbsp;**language**:`
- `location_city` -> `≡&nbsp;location_city:`
- `location_state` -> `≡&nbsp;location_state:`
- `references` -> `☰&nbsp;references:`
- `references (derived)` -> `☰&nbsp;references (derived):`
- `language_versions (derived)` -> `≡&nbsp;language versions (derived):`
