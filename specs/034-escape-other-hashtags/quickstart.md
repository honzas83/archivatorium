# Quickstart: Validation Guide

This document describes how to validate the selective hashtag escaping and capped index page features.

## Prerequisites
- Python 3.12 installed.
- Vault directories created for testing.

---

## Validation Scenario 1: Selective Hashtag Escaping

### Setup
1. Create a test markdown file `test_doc.md` inside a mock vault folder:
   ```markdown
   ---
   archive_code: PO/81/10
   language: English
   ---
   > [!info] Metadata
   > | ≡&nbsp;archive_code: | PO/81/10 |
   > | ☰&nbsp;references: | |

   > [!abstract]
   > # Test Document Title
   >
   > ## Categories/Topics
   > - #Topics/Defence/Planning
   >
   > ## Entities
   > - #Entities/Org/NATO

   # Page 1
   DOCUMENT DESTRUCTION MEMO. #67-87155
   Check the reference #67-8/9/50.
   Already escaped: \#67-8.
   ```

### Execution
Run the interlink command on the mock vault directory:
```bash
archivatorium interlink <mock_vault_dir>
```

### Expected Output
1. The `test_doc.md` is updated in-place.
2. The headers (`# Test Document Title` and `# Page 1`) are untouched.
3. Legitimate tags (`#Topics/Defence/Planning` and `#Entities/Org/NATO`) are untouched.
4. Non-canonical hashtags (`#67-87155` and `#67-8/9/50`) are escaped:
   ```markdown
   \#67-87155
   \#67-8/9/50
   ```
5. Already escaped `#` (`\#67-8`) is untouched (idempotency check: not escaped to `\\#67-8`).

---

## Validation Scenario 2: Index Capping and Search Links

### Setup
1. Create a mock vault with 55 separate markdown documents, each containing the tag `#Tags/DefencePlanning`.
2. Run the interlink command to rebuild the indices:
   ```bash
   archivatorium interlink <mock_vault_dir>
   ```

### Expected Output
1. The file `Index - Tags.md` is generated in the vault root.
2. Under the heading `### #Tags/DefencePlanning`:
   - Exactly **50** document wikilinks are listed.
   - An entry like the following is appended at the end of the tag's list:
     ```markdown
     - ... and 5 more. [Search in Vault](obsidian://search?vault=mock_vault_dir&query=tag:%23Tags/DefencePlanning)
     ```
3. No lag is experienced when opening `Index - Tags.md` in Obsidian.
