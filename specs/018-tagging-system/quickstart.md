# Quickstart: Precision Tagging System

## Workflow Overview
The Precision Tagging System operates in two distinct steps to maximize metadata accuracy and thematic coverage.

### Step 1: Primary Metadata Extraction
The system scans the **first 10k tokens** of the document to extract:
- Title, Summary, Abstract
- Document Date, Archive Code
- Sender, Recipient, Intent (for letters)

### Step 2: Comprehensive Tagging Pass
The system processes the document using a **Dynamic Pass** strategy:
1. **Token Check**: The system estimates the token count of the document.
2. **Single Pass**: If the document fits within the model's context window (e.g., < 32k tokens for `gemma4:31b`), all tags are extracted in a single pass.
3. **Sliding Window Fallback**: If the document is larger than the context window:
    - It is split into overlapping chunks (e.g., 28k tokens each).
    - Tags are extracted from each chunk using the non-thinking model (`think: false`).
    - Results are aggregated and deduplicated across all chunks.
4. **Final Refinement**: 
    - Keep top 10 most frequent conceptual tags.
    - Suppress any conceptual tag that is already represented as an Entity or Topic.
    - Normalize exercises to `Name/YY`.

## Output Example
The final Markdown file will contain a callout block like this:

> [!abstract]
> # Strategic Balance in the Mediterranean
> A detailed overview of maritime deployments in 1974.
> 
> ## Mentioned Entities
> State/Greece State/Turkey Org/NATO City/Italy/Naples
> 
> ## Categories/Topics
> Category/Geopolitics and Crises/Greece and Turkey Relations — Discussion of Aegean boundaries.
> 
> ## Tags
> #MaritimeSecurity #SACEUR #SouthernFlank #WINTEX/73
