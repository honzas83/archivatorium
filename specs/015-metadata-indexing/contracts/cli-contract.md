# CLI Contract: index subcommand

## Usage
`python -m ocrpolish.cli index INPUT_DIR [OPTIONS]`

## Arguments
- `INPUT_DIR`: Path to the Obsidian vault root containing processed `.md` files.

## Options
- `--output-xlsx`, `-o`: (Optional) Path to save the XLSX metadata index.
- `--topics-yaml`, `-t`: (Required if generating topic index) Path to the YAML file defining topic hierarchy and descriptions.
- `--recursive/--no-recursive`: (Default: True) Whether to scan subdirectories for documents.

## Outputs
1. `INPUT_DIR/Index - States.md`: Alphabetical list of #State/ tags.
2. `INPUT_DIR/Index - Cities.md`: State-grouped list of #City/ tags.
3. `INPUT_DIR/Index - Organizations.md`: List of #Org/ tags.
4. `INPUT_DIR/Index - Topics.md`: Hierarchical list of #Category/Topic tags with descriptions.
5. `output-xlsx`: (If specified) Spreadsheet containing all document metadata.
