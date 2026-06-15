# Tagging & Entity Extraction Analysis (v6)

This report analyzes the distribution and quality of the `#Tags`, `#Entities`, and `#Topics` generated in `NATO_NPG_metadata.v6`. It uses the data compiled in [COUNTS_v6.csv](../COUNTS_v6.csv) to identify vocabulary fragmentation and proposes prompt-based solutions.

---

## 📊 Summary Statistics

Across all documents in `NATO_NPG_metadata.v6/NPG - Nuclear Planning Group`:
* **Total Unique Tags/Entities/Topics**: 1,939
* **Total Occurrences**: 31,436

### Category Breakdown

| Category | Unique Count | Total Occurrences | Average Occurrences | Single-Occurrence Tags (Tail) |
| :--- | :---: | :---: | :---: | :---: |
| **Topic** (`#Topics/...`) | 47 | 4,314 | 91.79 | 2 (4.3%) |
| **Tag** (`#Tags/...`) | 518 | 13,727 | 26.50 | 282 (54.4%) |
| **Entity** (`#Entities/...`) | 1,374 | 13,395 | 9.75 | 970 (70.6%) |

### Frequency Distribution by Category

- **Topics**:
  - 1 occurrence: 2 (4.3%)
  - 2-5 occurrences: 9 (19.1%)
  - 6-20 occurrences: 14 (29.8%)
  - 21+ occurrences: 22 (46.8%)
- **Tags**:
  - 1 occurrence: 282 (54.4%)
  - 2-5 occurrences: 110 (21.2%)
  - 6-20 occurrences: 56 (10.8%)
  - 21+ occurrences: 70 (13.5%)
- **Entities**:
  - 1 occurrence: 970 (70.6%)
  - 2-5 occurrences: 265 (19.3%)
  - 6-20 occurrences: 73 (5.3%)
  - 21+ occurrences: 66 (4.8%)

---

## 🔍 Deep-Dive: Vocabulary Fragmentation & Duplicate Analysis

The statistics show a very **long tail of single-occurrence tags**, especially in the **Entities** category (70.6%). This indicates vocabulary fragmentation. The major patterns of duplication and corruption found in `COUNTS_v6.csv` are:

### 1. Casing Mismatches (LLM Case Inconsistency)
Although the python utility standardizes path structures, it preserves original casing. The LLM regularly outputs case variations for identical entities:
* **NATO**: `#Entities/Org/NATO` (788) vs. `#Entities/Org/nato` (96)
* **NPG Staff Group**: `#Entities/Org/Nuclear-Planning-Group-Staff-Group` (1063) vs. `#Entities/Org/nuclear-planning-group-staff-group` (100) vs. `#Entities/Org/NUCLEAR-PLANNING-GROUP-STAFF-GROUP` (3)
* **USA / United States**: `#Entities/State/United-States` (458) vs. `#Entities/State/united-states` (29) vs. `#Entities/State/USA` (62) vs. `#Entities/State/usa` (4)

### 2. OCR Corruption Surviving as Entities
During OCR processing, certain words are misread (e.g. `Staff` read as `ST/FF`, `St-1F`, or `Sta-F`). The LLM extracts these literally as distinct entities:
* `#Entities/Org/Nuclear-Planning-Group-Staff-Group` (1,063)
* ❌ `#Entities/Org/Nuclear-Planning-Group-ST/FF-Group` (1)
* ❌ `#Entities/Org/Nuclear-Planning-Group-Sta-F-Groupe` (1)
* ❌ `#Entities/Org/Nuclear-Planning-Group-STA-F-Group` (1)
* ❌ `#Entities/Org/Nuclear-Planning-Group-St-1F-Group` (1)
* ❌ `#Entities/Org/Nuclear-Planning-Group-S-U-F-Group` (1)
* ❌ `#Entities/Org/Nuclear-Planning-Group-State-Group` (1)

### 3. Multilingual Duplicates (French vs. English)
Since the corpus contains both English and French documents, entity names are extracted in the language of the source text, creating duplicates:
* **Cities**: `#Entities/City/UK/London` (92) vs. `#Entities/City/UK/Londres` (9)
* **Cities**: `#Entities/City/Belgium/Brussels` (1,211) vs. `#Entities/City/Belgium/Bruxelles` (144)
* **Cities**: `#Entities/City/Netherlands/La-Haye` (5) vs. `#Entities/City/Netherlands/The-Hague`
* **States**: `#Entities/State/Germany` (196) vs. `#Entities/State/Allemagne` (5)
* **States**: `#Entities/State/United-Kingdom` (306) vs. `#Entities/State/Royaume-Uni` (5)
* **Organisations**: `#Entities/Org/NATO` (788) vs. `#Entities/Org/OTAN` (4) vs. `#Entities/Org/Organisation-du-Trait-de-l-Atlantique-Nord` (4)

### 4. Hierarchical Country Code Inconsistency & Structural Errors
The `City/<state>/<city>` structure (where `<state>` represents the country) suffers from structural confusion:
* **Alternative Country Keys**: `#Entities/City/England/London` (1) vs. `#Entities/City/UK/London` (92)
* **Region/State Mixups**: `#Entities/City/USA/Florida` (treating the state of Florida as a city) vs. `#Entities/State/USA/California` (nesting a state inside a state)

---

## 💡 Proposed Prompt Options

Below are two options for updating the tagging instructions in [tagging_service.py](../ocrpolish/services/tagging_service.py).

### Option 1: Lightweight Prompt Hardening
This option adds concise, imperative rules to the end of the existing categories and critical rules.

```diff
     def _generate_tagging_prompt(self, text: str, reuse_hints: Any | None = None) -> str:
         """
         Generates the prompt for the tagging pass.
         """
         reuse_hint_text = self._format_reuse_hints(reuse_hints)
         reuse_section = f"\n\n{reuse_hint_text}\n" if reuse_hint_text else "\n"
         return (
             "Document Excerpt:\n\n"
             f"{text}\n\n"
             "Based on the content above, extract precision tags in three categories:\n\n"
             "1. 'entity_tags': Hierarchical tags for mentioned entities. "
-            "Use formats: State/<name>, Org/<name>, City/<state>/<city>, Person/<name>.\n"
+            "Use formats: State/<name>, Org/<name>, City/<state>/<city>, Person/<name>.\n"
+            "   - MANDATORY: Always translate and extract entity names (States, Orgs, Cities) in English to ensure cross-document consistency (e.g. use 'Germany' instead of 'Allemagne', 'Brussels' instead of 'Bruxelles', 'The Hague' instead of 'La Haye').\n"
+            "   - MANDATORY: Strip or transliterate diacritics/accents from names (e.g., use 'Geneve' instead of 'Genève', 'Oberammergau' instead of 'Oberammergau') to prevent normalization issues.\n"
+            "   - Prefer standard abbreviations/acronyms for well-known organisations (e.g., use 'NATO' instead of 'North-Atlantic-Treaty-Organization', 'SHAPE' instead of 'Supreme-Headquarters-Allied-Powers-Europe', 'NPG' instead of 'Nuclear-Planning-Group').\n"
+            "   - Correct obvious OCR spelling typos in entity names using context (e.g., correct 'Fuldah' to 'Fulda').\n"
             "2. 'topic_tags': Select every clearly justified taxonomy topic from the "
             "flat taxonomy below. Use format: Category/Topic. Include a brief 'reason' "
             "for each.\n"
             "   MANDATORY: When providing a 'reason', include direct citations in double "
             "quotes from the text to justify the topic selection.\n"
             "3. 'conceptual_tags': Required canonical tag paths for archivally substantive "
             f"concepts. Return at least {MIN_SUBSTANTIVE_CONCEPTUAL_TAGS} conceptual tags "
             "for substantive documents; include "
             "every clearly justified useful conceptual tag; return an empty list only for "
             "non-substantive administrative stubs. "
             "PRIORITIZE re-using tags from the vocabularies below. Normalize exercises as Name/YY. "
             "MANDATORY: Include all all-caps abbreviations mentioned in the text "
             "when they are meaningful acronyms.\n\n"
             "APPROVED TAXONOMY (YAML):\n"
             f"{self.taxonomy_prompt_text}\n\n"
             "EXISTING VOCABULARY (USEFUL TAGS):\n"
             f"{self.useful_tags_prompt_text}"
             f"{reuse_section}\n"
             "CRITICAL RULES:\n"
             "- Only include tags that are clearly justified by the text.\n"
             "- Exclude routine administrative labels (agenda, report, notice, corrigendum).\n"
             "- Ensure hierarchical formats are strictly followed.\n"
+            "- Always format names of States, Cities, Persons, and Organisations in Title Case (e.g., 'United-States', 'Netherlands', 'Brussels'), preserving ALL CAPS only for standard acronyms (e.g., 'NATO', 'SHAPE', 'NPG', 'SACLANT'). Never output entities in lowercase.\n"
             "- Conceptual tags must not be exact duplicates of entity names or topic components, "
             "but preserve substantive archival concepts even when related entities or topics exist.\n"
             "- If an entity or concept is in ALL-CAPS but is NOT an abbreviation "
             "(e.g., PERSHING), generate the tag in Title Case (e.g., Pershing)."
         )
```

---

### Option 2: Explicit Normalization Prompt with Few-Shot Examples (Highly Detailed)
This option reorganizes the prompt to include explicit translation tables, typo-correction instructions matching against preferred vocabulary, and few-shot examples to maximize LLM alignment.

```diff
     def _generate_tagging_prompt(self, text: str, reuse_hints: Any | None = None) -> str:
         """
         Generates the prompt for the tagging pass.
         """
         reuse_hint_text = self._format_reuse_hints(reuse_hints)
         reuse_section = f"\n\n{reuse_hint_text}\n" if reuse_hint_text else "\n"
         return (
             "Document Excerpt:\n\n"
             f"{text}\n\n"
             "Based on the content above, extract precision tags in three categories:\n\n"
             "1. 'entity_tags': Hierarchical tags for mentioned entities. "
-            "Use formats: State/<name>, Org/<name>, City/<state>/<city>, Person/<name>.\n"
+            "Use formats: State/<name>, Org/<name>, City/<state>/<city>, Person/<name>.\n"
+            "   Strict Normalization Rules for Entities:\n"
+            "   - Translate to English: Always extract country and city names in English (e.g., 'Germany', 'United-Kingdom', 'United-States', 'Brussels', 'The-Hague'). Never use French or native variations ('Allemagne', 'Royaume-Uni', 'USA', 'UK', 'Bruxelles', 'La-Haye').\n"
+            "   - Title Case: Always use Title Case for State, City, Person, and Organisation names. Preserve ALL CAPS only for standard acronyms (e.g. 'NATO', 'SHAPE', 'NPG', 'SACLANT', 'DPC'). Do not use lowercase.\n"
+            "   - Strip Accents: Strip or transliterate diacritics (e.g., 'Genève' becomes 'Geneve', 'München' becomes 'Munich').\n"
+            "   - Organisation Acronym Priority: Prefer short acronyms for well-known organisations: 'NATO' (not 'North-Atlantic-Treaty-Organization'), 'SHAPE' (not 'Supreme-Headquarters-Allied-Powers-Europe'), 'NPG' (not 'Nuclear-Planning-Group'), 'NPG-Staff-Group' (not 'Nuclear-Planning-Group-Staff-Group').\n"
+            "   - OCR Recovery: If an entity name contains spelling anomalies typical of OCR corruption (e.g., 'Nuclear-Planning-Group-ST/FF-Group' or 'Fuldah'), correct them to their standard form ('Nuclear-Planning-Group-Staff-Group', 'Fulda') by cross-referencing the text with the preferred vocabularies below.\n"
             "2. 'topic_tags': Select every clearly justified taxonomy topic from the "
             "flat taxonomy below. Use format: Category/Topic. Include a brief 'reason' "
             "for each.\n"
             "   MANDATORY: When providing a 'reason', include direct citations in double "
             "quotes from the text to justify the topic selection.\n"
             "3. 'conceptual_tags': Required canonical tag paths for archivally substantive "
             f"concepts. Return at least {MIN_SUBSTANTIVE_CONCEPTUAL_TAGS} conceptual tags "
             "for substantive documents; include "
             "every clearly justified useful conceptual tag; return an empty list only for "
             "non-substantive administrative stubs. "
             "PRIORITIZE re-using tags from the vocabularies below. Normalize exercises as Name/YY. "
             "MANDATORY: Include all all-caps abbreviations mentioned in the text "
             "when they are meaningful acronyms.\n\n"
+            "EXAMPLES OF CORRECT EXTRACTIONS:\n"
+            "- Text: 'Un compte rendu de la réunion à Bruxelles...'\n"
+            "  -> entity_tags: ['City/Belgium/Brussels']\n"
+            "- Text: 'agreed by l\\'OTAN and SACEUR'\n"
+            "  -> entity_tags: ['Org/NATO', 'Org/SACEUR']\n"
+            "- Text: 'represented by Royaume-Uni and USA'\n"
+            "  -> entity_tags: ['State/United-Kingdom', 'State/United-States']\n"
+            "- Text: 'The Nuclear Planning Group Staff Group met at Fuldah...'\n"
+            "  -> entity_tags: ['Org/NPG-Staff-Group', 'City/Germany/Fulda']\n"
+            "- Text: 'discussions on the PERSHING missile system...'\n"
+            "  -> conceptual_tags: ['Pershing']\n\n"
             "APPROVED TAXONOMY (YAML):\n"
             f"{self.taxonomy_prompt_text}\n\n"
             "EXISTING VOCABULARY (USEFUL TAGS):\n"
             f"{self.useful_tags_prompt_text}"
             f"{reuse_section}\n"
             "CRITICAL RULES:\n"
             "- Only include tags that are clearly justified by the text.\n"
             "- Exclude routine administrative labels (agenda, report, notice, corrigendum).\n"
             "- Ensure hierarchical formats are strictly followed.\n"
             "- Conceptual tags must not be exact duplicates of entity names or topic components, "
             "but preserve substantive archival concepts even when related entities or topics exist.\n"
             "- If an entity or concept is in ALL-CAPS but is NOT an abbreviation "
             "(e.g., PERSHING), generate the tag in Title Case (e.g., Pershing)."
         )
```
