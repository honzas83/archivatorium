# Workshop Prompt: Building an LLM Metadata Extractor

## Step 1: Base Extractor

You are an expert Python developer. Your task is to write a simple, standalone CLI script that uses the `ollama` Python library to extract structured metadata from a Markdown document and prepends it as YAML frontmatter.

### Requirements

1. **Dependencies**: The script should only require `ollama`, `pydantic`, `pyyaml`, and standard library modules (`argparse`, `pathlib`).
2. **Schema**: Use Pydantic to define a `MetadataSchema` with the following fields:
   - `title` (string): The document title.
   - `summary` (string): A 2-sentence summary.
   - `date` (string): The document date in ISO format (YYYY-MM-DD).
   - `tags` (list of strings): 3-5 descriptive hashtags without spaces (e.g., `#History`).
3. **Execution**:
   - The script should accept an input file path and an output file path via command-line arguments.
   - Read the input Markdown file.
   - Use `ollama.chat` with the `gemma4:26b` model (or similar) to extract the metadata, passing the Pydantic schema using the `format=MetadataSchema.model_json_schema()` parameter.
   - Convert the extracted JSON into YAML format.
   - Prepend the YAML block (wrapped in `---`) to the original Markdown content.
   - Save the result to the output file path.
4. **Resilience**: Ensure the script handles basic errors (e.g., file not found, Ollama server unreachable).

### Expected Output
Please provide the complete, runnable Python code in a single file block. Include brief comments explaining how the Ollama integration and Pydantic schema work together.

---

## Step 2: Expanding the Schema (Author and Location)

Modify the existing script to extract more detailed information about the document's origins.

### Requirements
1. **Update the Schema**: Add the following fields to your `MetadataSchema`:
   - `author_name` (string): The name of the individual who wrote the document. If missing, leave empty.
   - `author_institution` (string): The organization or institution responsible for the document.
   - `location_city` (string): The city where the document originated.
   - `location_state` (string): The nation-state where the document originated.
2. **Contextual Instruction**: Update the prompt to the LLM to instruct that if `location_city` is identified (e.g., "Brussels"), the `location_state` should be inferred (e.g., "Belgium").
3. **Output**: Ensure the new fields are correctly parsed and added to the YAML frontmatter below the summary and date.

---

## Step 3: Handling Complex Structures (Correspondence)

Archival documents often take the form of letters, memos, or direct correspondence. Add the ability to extract sender and recipient details.

### Requirements
1. **Update the Schema**: Add the following flattened fields to your `MetadataSchema` to handle correspondence (flattened fields are used to prevent nested object grammar issues in some local LLMs):
   - `correspondence_sender` (string): The name and/or institution of the sender.
   - `correspondence_recipient` (string): The name and/or institution of the recipient.
   - `correspondence_transaction` (string): The specific action, request, or purpose imposed by the letter.
2. **Filtering Logic**: Modify the script so that if the document is NOT a letter, or if the LLM returns empty values for all three fields, the correspondence data is entirely omitted from the final YAML output.
3. **Nesting in YAML**: In the final YAML output, reconstruct these flattened fields into a clean, nested `correspondence` dictionary block.