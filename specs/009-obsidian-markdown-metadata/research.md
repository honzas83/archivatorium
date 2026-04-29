# Research: Obsidian Markdown Metadata

## Findings

### 1. Flattening Logic
- **Decision**: Nested dictionaries (like the `correspondence` block currently created in `MetadataProcessor`) must be flattened using underscores.
- **Rationale**: User preference and Obsidian's Properties view compatibility.
- **Implementation**: Instead of creating a `correspondence` dict, use the `correspondence_sender`, `correspondence_recipient`, and `correspondence_transaction` fields directly as top-level keys in the `metadata_dict`.

### 6. Abstract Callout
- **Decision**: Use Obsidian's `[!abstract]` callout syntax.
- **Rationale**: User requested highly visible abstract at the start of the document body.
- **Implementation**: Create a helper function to wrap text in callout blocks: `> [!abstract] Abstract\n> <content>`. Insert this after the frontmatter and before the main text.

### 2. Obsidian Tag Format
- **Decision**: Remove the `#` prefix from tags when placing them in the `tags` YAML property.
- **Rationale**: Obsidian's YAML frontmatter convention for the `tags` property is to use plain strings. The `#` is added automatically by Obsidian's UI.
- **Implementation**: `[tag.lstrip('#') for tag in tags]`

### 3. Source PDF Linking (Relative Paths)
- **Decision**: Use a `source` property in the YAML frontmatter containing an Obsidian internal link with a relative path.
- **Rationale**: User preference for "Option B" from clarification. Allows PDFs to reside in a different directory from the Markdown notes while remaining linkable in Obsidian.
- **Implementation**: 
    - Introduce a `--vault-root` parameter (optional) to the CLI.
    - If `--vault-root` is provided, the system will calculate the path from the vault root to the source PDF.
    - If the PDF directory is separate, a `--pdf-dir` parameter could also be used to locate the actual files if they don't match the input `.md` structure.
    - **Calculated Link**: `[[<relative_path_to_pdf>]]`

### 4. Output File Format
- **Decision**: Continue using `.md` files with YAML frontmatter, but ensure no nesting.
- **Rationale**: Maintains compatibility with the existing `MetadataProcessor` while fulfilling the "suit Obsidian" requirement.

### 5. Tag Consistency
- **Decision**: Maintain the `tag_counts` logic but ensure the context passed to the LLM also follows the no-space/hashtag convention, while the final output strips the `#`.

## Alternatives Considered
- **Filename Only**: Rejected in favor of relative paths for cross-directory support.
- **Link in body**: Rejected per user preference for frontmatter property.
- **Nested properties**: Rejected as Obsidian doesn't handle them well in the Properties UI.

## Unresolved Items (Now Resolved)
- **Vault Root**: Will be an optional CLI argument to support relative path calculation.
- **Key Collisions**: Flattening `correspondence_sender` etc. is already safe as these keys are unique in the `MetadataSchema`.
