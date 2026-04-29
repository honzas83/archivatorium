# LLM Metadata Extraction & Topic Detection Workflow

This document provides a detailed technical overview of how `ocrpolish` utilizes Large Language Models (LLMs) via Ollama to extract structured metadata and detect hierarchical topics from OCR-processed documents.

## Table of Contents
1. [Architectural Overview](#architectural-overview)
2. [Primary Metadata Extraction](#primary-metadata-extraction)
3. [Two-Step Topic Detection](#two-step-topic-detection)
4. [Prompt Engineering Strategies](#prompt-engineering-strategies)
5. [Context Window Management](#context-window-management)
6. [Obsidian Integration & Formatting](#obsidian-integration--formatting)

---

## Architectural Overview

`ocrpolish` uses a sequential, multi-pass LLM workflow to transform noisy OCR text into rich, structured Obsidian Markdown files. The system interfaces with a local Ollama instance (default model: `gemma4:26b`) using Pydantic schemas for guaranteed structured output.

The workflow follows these stages:
1. **Pass 1: Primary Metadata**: Extracts title, summary, abstract, dates, and actors.
2. **Pass 2 (Optional): Topic Detection**: Performs a two-step classification against a YAML hierarchy.
3. **Pass 3: Formatting**: Reworks the extracted data into YAML frontmatter and an Obsidian-styled "Abstract" callout.

---

## Primary Metadata Extraction

The first pass focuses on general document understanding. It reads a significant portion of the document (up to 10kB) to fill a comprehensive `MetadataSchema`.

### Extracted Fields
- **Standard Identifiers**: Title, Archive Code, Language.
- **Temporospatial**: Complete official date (YYYY-MM-DD), City, State.
- **Narrative**: One-sentence summary, Detailed abstract (up to 20 sentences).
- **Actors**: Sender, Recipient, Transaction details (for correspondence).
- **Entities**: Mentioned states and organizations.
- **Tags**: A list of 3-8 flat tags for general indexing.

### Hallucination Prevention
If a document is large (>12kB) and the date is missing from the first chunk, the system performs a targeted **Secondary Date Pass** on the final 10kB of the file to locate official dates typically found at the document's end.

---

## Two-Step Topic Detection

When a hierarchy YAML (e.g., `NATO_themes.yaml`) is provided, `ocrpolish` performs a high-precision categorization process.

### Step 1: Category Selection
The LLM is presented with the raw 10kB document excerpt and a list of high-level categories (including their descriptions) from the hierarchy. It selects only the categories that apply.

### Step 2: Topic Assignment
For the selected categories, the LLM is presented with all sub-topics, including:
- Detailed topic descriptions.
- **Positive Anchors**: Keywords/concepts that strongly suggest a match.
- **Negative Anchors**: Keywords/concepts that should exclude a match.

### Constraints & Selectivity
- **Limit**: At most 3 most important topics are assigned (enforced via Pydantic).
- **Reasoning**: The model MUST provide a specific, non-generic reason for every assignment.
- **Quality over Quantity**: The model is instructed to be selective, especially for documents shorter than 3 pages, and to avoid "over-filling" the 3 available slots.
- **Isolation**: To prevent "hallucination loops," topic extraction relies strictly on the raw document excerpt, ignoring Pass 1 metadata (summary/abstract).

---

## Prompt Engineering Strategies

The system uses several advanced prompting techniques:
- **Title Case Correction**: Instructs the LLM to correct ALL CAPS text to Title Case while preserving NATO acronyms.
- **OCR Correction**: Encourages the model to use context to interpret and correct OCR errors during extraction.
- **Negative Instruction**: Explicitly forbids generic reasoning like "it is relevant to the context."
- **Structured Pydantic Output**: All prompts are wrapped in requests for JSON objects matching internal Pydantic models, ensuring the CLI can reliably parse the LLM's response.

---

## Context Window Management

The context window is optimized for both speed and precision:
- **`CHUNK_SIZE`**: 10,000 characters (approx. 10kB).
- **`LARGE_DOC_THRESHOLD`**: 12,000 characters.
- **Text Selection**: The system prioritizes the beginning of the document (Pass 1 & 2) but can pivot to the end (Secondary Date Pass) to ensure no critical metadata is missed.

---

## Obsidian Integration & Formatting

The extracted data is formatted specifically for Obsidian:

### YAML Frontmatter
Clean metadata (title, sender, date, etc.) is stored here for standard searchability. **Tags are excluded from frontmatter to prevent clutter.**

### Abstract Callout (`[!abstract]`)
All narrative and categorization data is moved here:
1. **Title**: Rendered as an H1 header.
2. **Abstract**: The detailed document overview.
3. **## Categories/Topics**: A list of hierarchical tags and justifications (e.g., `#Category/Topic — Specific Reason`).
4. **## Tags**: The flat tags from Pass 1, rendered inline and prefixed with `#`.

This layout ensures that the document is informative and navigable immediately upon opening in Obsidian.
