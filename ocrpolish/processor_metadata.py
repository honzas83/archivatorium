import logging
from collections import Counter
from pathlib import Path

from ocrpolish.models.metadata import LastDateSchema, MetadataSchema
from ocrpolish.services.ollama_client import OllamaClient
from ocrpolish.utils.metadata import (
    flatten_metadata,
    format_as_callout,
    normalize_obsidian_tags,
    prepend_frontmatter,
)

logger = logging.getLogger(__name__)

# Constants for context window management
CHUNK_SIZE = 6000
LARGE_DOC_THRESHOLD = 8000

class MetadataProcessor:
    def __init__(
        self, 
        ollama_client: OllamaClient, 
        output_dir: Path, 
        overwrite: bool = False,
        vault_root: Path | None = None,
        pdf_dir: Path | None = None
    ):
        self.client = ollama_client
        self.output_dir = output_dir
        self.overwrite = overwrite
        self.vault_root = vault_root
        self.pdf_dir = pdf_dir
        self.tag_counts = Counter()

    def _get_pdf_link(self, input_file: Path) -> str:
        """Calculates the Obsidian-style link to the source PDF."""
        pdf_filename = f"{input_file.stem}.pdf"
        if not self.vault_root:
            return f"[[{pdf_filename}]]"

        try:
            pdf_path = input_file.with_suffix(".pdf")
            if self.pdf_dir:
                pdf_path = self.pdf_dir / pdf_filename

            relative_pdf_path = pdf_path.relative_to(self.vault_root)
            return f"[[{relative_pdf_path.as_posix()}]]"
        except Exception as e:
            logger.warning(f"Could not calculate relative path to PDF: {e}")
            return f"[[{pdf_filename}]]"

    def _prepare_obsidian_metadata(self, raw_dict: dict, input_file: Path) -> dict:
        """Prepares the metadata dictionary for Obsidian output."""
        # 1. Standardize tags
        if raw_dict.get("tags"):
            raw_dict["tags"] = normalize_obsidian_tags(raw_dict["tags"])

        # 2. Add source PDF link
        raw_dict["source"] = self._get_pdf_link(input_file)

        # 3. Define primary field order and extract them
        primary_keys = [
            "title",
            "summary",
            "abstract",
            "author_name",
            "author_institution",
            "date",
            "archive_code",
            "language",
            "location_city",
            "location_state",
            "source",
        ]

        metadata_dict = {}
        for k in primary_keys:
            if k in raw_dict:
                metadata_dict[k] = raw_dict.pop(k)

        # 4. Flatten the remaining fields
        flattened_remainder = flatten_metadata(raw_dict)
        metadata_dict.update(flattened_remainder)
        return metadata_dict

    def process_file(
        self, input_file: Path, output_file: Path, frequent_tags: list[str] | None = None
    ) -> bool:
        """
        Processes a single file: extracts metadata and writes to output.
        """
        if output_file.exists() and not self.overwrite:
            logger.info(f"Skipping {input_file} (output already exists)")
            return False

        try:
            content = input_file.read_text(encoding="utf-8")

            # Prepare tag context if available
            tag_context = ""
            if frequent_tags:
                tag_context = (
                    f"\nIMPORTANT: Prioritize using these existing tags for consistency: "
                    f"{', '.join(frequent_tags)}. "
                    "Only create new tags if the current list is not sufficient."
                )

            # Phase 1: Primary Extraction (First chunk)
            first_chunk = content[:CHUNK_SIZE]
            prompt = (
                f"Source Filename: {input_file.name}\n\n"
                f"Document Content (First Part):\n\n{first_chunk}\n\n"
                "Please extract metadata following these strict rules:\n"
                "1. 'title' must be extracted carefully. It is usually on the first page, "
                "but could also be part of the second page. The title should make sense "
                "in the context of the summary and abstract.\n"
                "2. 'summary' must be exactly two sentences. It must be an independent entity.\n"
                "3. 'abstract' must be a detailed overview, limited to at most 20 sentences. "
                "It must be a superset of the summary.\n"
                "4. 'mentioned_states' must only contain full names of nation states.\n"
                "5. 'mentioned_organisations' should include international bodies.\n"
                "6. 'date' must be the complete official document date (YYYY-MM-DD).\n"
                "7. 'archive_code' should be derived using both the text and the filename.\n"
                "8. If the document is a letter, describe 'sender', 'recipient', "
                "and 'transaction'.\n"
                "9. 'references' should contain a list of any other reference codes.\n"
                "10. IMPORTANT: Convert certain fields to Title Case if found in ALL CAPS. "
                "Preserve uppercase for NATO acronyms.\n"
                "11. Ensure 'location_state' is filled if 'location_city' is identified.\n"
                "12. Generate between 3 and 8 'tags'. No spaces.\n"
                "13. Interpret and correct OCR errors using context."
                f"{tag_context}"
            )

            metadata_obj = self.client.extract_structured(prompt, MetadataSchema)

            # Update tag counts for future consistency
            if metadata_obj.tags:
                self.tag_counts.update(metadata_obj.tags)

            # Convert to dict.
            raw_dict = metadata_obj.model_dump()

            # Phase 2: Secondary Pass for Date (only if missing and document is large)
            if not raw_dict.get("date") and len(content) > LARGE_DOC_THRESHOLD:
                logger.info(
                    f"Date missing from first chunk of {input_file.name}. Scanning end..."
                )
                last_chunk = content[-CHUNK_SIZE:]
                date_prompt = (
                    f"Document Content (Final Part):\n\n{last_chunk}\n\n"
                    "Extract ONLY the complete official date (YYYY-MM-DD)."
                )
                try:
                    date_obj = self.client.extract_structured(date_prompt, LastDateSchema)
                    if date_obj.date:
                        raw_dict["date"] = date_obj.date
                        logger.info(f"Found date at end of document: {date_obj.date}")
                except Exception as e:
                    logger.warning(f"Secondary date extraction failed: {e}")

            # Prepare metadata for Obsidian
            metadata_dict = self._prepare_obsidian_metadata(raw_dict, input_file)

            # Insert Abstract Callout (User Story 4)
            abstract_text = metadata_dict.get("abstract", "")
            if abstract_text:
                callout = format_as_callout(abstract_text)
                content = callout + content

            # Prepend metadata to original content
            new_content = prepend_frontmatter(content, metadata_dict)

            # Ensure output is .md (Task T010)
            output_file = output_file.with_suffix(".md")
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(new_content, encoding="utf-8")
            return True
        except Exception as e:
            logger.error(f"Error processing {input_file}: {e}")
            return False

    def get_files(self, input_dir: Path, recursive: bool = True) -> list[Path]:
        """
        Returns a list of all .md files to be processed, excluding sidecar .filtered.md files.
        """
        pattern = "**/*.md" if recursive else "*.md"
        all_files = input_dir.glob(pattern)
        return [f for f in all_files if not f.name.endswith(".filtered.md")]

    def process_directory(self, input_dir: Path, recursive: bool = True) -> None:
        """
        Traverses directory and processes all .md files in alphabetical order.
        """
        files = sorted(self.get_files(input_dir, recursive))
        logger.info(f"Found {len(files)} markdown files in {input_dir}")
        
        for input_file in files:
            relative_path = input_file.relative_to(input_dir)
            output_file = self.output_dir / relative_path
            
            # Get 50 most frequent tags
            frequent_tags = [tag for tag, _ in self.tag_counts.most_common(50)]
            self.process_file(input_file, output_file, frequent_tags)
