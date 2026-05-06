# Quickstart: Metadata Citations

This feature automatically adds a citation block to the end of every generated Obsidian Markdown file.

## How it works

When you run the `metadata` command, the system extracts document details and formats them into three common citation styles:

1. **Chicago**
2. **Harvard**
3. **BibTeX**

These are placed in an Obsidian callout at the bottom of the file.

## Example Output

```markdown
... (document content) ...

> [!citing this document]
> **Chicago**:
> ```
> John, Doe, “NATO Defense Strategy 1968,” 1968/05/12, NATO Headquarters, NPG(SG)N(68)1, NATO Archive Obsidian, https://nato-obsidian.kky.zcu.cz/NPG(SG)N(68)1, 2026-05-06.
> ```
>
> **Harvard**:
> ```
> Doe, J. (1968). “NATO Defense Strategy 1968,” NATO Headquarters, NPG(SG)N(68)1, NATO Archive Obsidian, https://nato-obsidian.kky.zcu.cz/NPG(SG)N(68)1, 2026-05-06.
> ```
>
> **BibTeX**:
> ```
> @misc{NPG(SG)N(68)1,
>   author = {Doe, John},
>   title = {NATO Defense Strategy 1968},
>   year = {1968},
>   month = {May},
>   day = {12},
>   note = {NATO Headquarters, NPG(SG)N(68)1, NATO Archive Obsidian},
>   url = {https://nato-obsidian.kky.zcu.cz/NPG(SG)N(68)1},
>   urldate = {2026-05-06}
> }
> ```
```

## Configuration

- **Platform Name**: Default is `NATO Archive Obsidian`.
- **URL**: Default is `https://nato-obsidian.kky.zcu.cz/[ArchiveCode]`.
