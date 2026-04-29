import logging
import re
from collections import Counter
from pathlib import Path
from typing import Any

from ocrpolish.models.metadata import LastDateSchema, MetadataSchema
from ocrpolish.services.ollama_client import OllamaClient
from ocrpolish.services.topics_service import TopicExtractor
from ocrpolish.utils.metadata import (
    flatten_metadata,
    format_as_callout,
    format_hierarchical_tag,
    normalize_obsidian_tags,
    parse_frontmatter,
    stringify_frontmatter,
)

logger = logging.getLogger(__name__)

# Constants for context window management
CHUNK_SIZE = 10000
LARGE_DOC_THRESHOLD = 12000


class MetadataProcessor:
    def __init__(
        self,
        ollama_client: OllamaClient,
        output_dir: Path,
        overwrite: bool = False,
        vault_root: Path | None = None,
        pdf_dir: Path | None = None,
        topic_extractor: TopicExtractor | None = None,
    ):
        self.client = ollama_client
        self.output_dir = output_dir
        self.overwrite = overwrite
        self.vault_root = vault_root
        self.pdf_dir = pdf_dir
        self.topic_extractor = topic_extractor
        self.tag_counts: Counter[str] = Counter()

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

    def _prepare_obsidian_metadata(
        self, raw_dict: dict[str, Any], input_file: Path
    ) -> dict[str, Any]:
        """Prepares the metadata dictionary for Obsidian output."""
        # 1. Strip 'correspondence_' prefix from all keys
        clean_dict: dict[str, Any] = {}
        for k, v in raw_dict.items():
            new_key = k.removeprefix("correspondence_")
            clean_dict[new_key] = v
        raw_dict = clean_dict

        # 2. Standardize tags
        if raw_dict.get("tags"):
            raw_dict["tags"] = normalize_obsidian_tags(raw_dict["tags"])

        # 3. Add source PDF link
        raw_dict["source"] = self._get_pdf_link(input_file)

        # 4. Define primary field order and extract them
        primary_keys = [
            "title",
            "summary",
            "abstract",
            "sender",
            "recipient",
            "transaction",
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
                val = raw_dict.pop(k)
                # Only add if value is not "empty"
                if val not in (None, "", [], {}):
                    metadata_dict[k] = val

        # 5. Flatten the remaining fields and filter them
        flattened_remainder = flatten_metadata(raw_dict)
        for k, v in flattened_remainder.items():
            if v not in (None, "", [], {}):
                metadata_dict[k] = v
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

            # 1. Separate existing frontmatter from body
            existing_metadata, original_body = parse_frontmatter(content)

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
                "2. 'summary' must be exactly one sentence. It must be an independent entity.\n"
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
                logger.info(f"Date missing from first chunk of {input_file.name}. Scanning end...")
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

            # Prepare metadata for Obsidian (standardization, flattening, prefix removal)
            # We merge with existing metadata here
            combined_raw = {**existing_metadata, **raw_dict}
            metadata_dict = self._prepare_obsidian_metadata(combined_raw, input_file)

            # User Story 2: Move title and abstract to body callout
            # We keep title in frontmatter for searchability (as requested), 
            # but move abstract exclusively to the body.
            title = metadata_dict.get("title", "")
            abstract = metadata_dict.pop("abstract", "")

            # US-011: Perform topic extraction if extractor is provided
            topic_list_items = []
            if self.topic_extractor and abstract:
                assignments = self.topic_extractor.extract_topics(first_chunk)
                if assignments:
                    for a in assignments:
                        tag = format_hierarchical_tag(a.category, a.topic)
                        topic_list_items.append(f"{tag} — {a.reason}")

            # US3: Extract flat tags and remove from frontmatter property
            flat_tags = metadata_dict.pop("tags", [])
            flat_tags_str = ""
            if flat_tags:
                # Add # to flat tags for body callout (inline)
                flat_tags_str = " ".join([f"#{t}" if not t.startswith("#") else t for t in flat_tags])

            # Build the callout block with dedicated sections for topics and tags
            body_prefix = ""
            if title or abstract or topic_list_items or flat_tags_str:
                sections = []
                if title:
                    sections.append(f"# {title}")
                if abstract:
                    sections.append(abstract)
                
                if topic_list_items:
                    topic_section = "## Categories/Topics\n\n" + "\n".join(topic_list_items)
                    sections.append(topic_section)
                
                if flat_tags_str:
                    sections.append(f"## Tags\n\n{flat_tags_str}")

                callout_body = "\n\n".join(sections)

                # Wrap in callout
                body_prefix = format_as_callout(
                    callout_body.strip(), title="", callout_type="abstract"
                )

            # Combine everything: [Frontmatter] + [Callout] + [Original Body]
            frontmatter_str = stringify_frontmatter(metadata_dict)

            # Clean up original body: remove leading whitespace and any horizontal rules
            # or duplicate titles that might cause clutter
            original_body = original_body.lstrip()

            # Pattern to match horizontal rules or headers that match the title
            # (e.g., "---", "# Title", "## Title")
            while True:
                start_len = len(original_body)

                # Remove horizontal rules
                if original_body.startswith("---"):
                    original_body = re.sub(r"^---\s*", "", original_body)

                # Remove title headers
                if title:
                    # Escape title for regex
                    escaped_title = re.escape(title)
                    # Match optional header symbols, the title, and optional following space/newline
                    original_body = re.sub(
                        rf"^(#+\s+)?{escaped_title}\s*\n?", "", original_body, flags=re.IGNORECASE
                    )

                # If length didn't change, we're done cleaning
                if len(original_body) == start_len:
                    break
                original_body = original_body.lstrip()

            # Construct final content with proper spacing
            # frontmatter_str ends with \n, so we add another \n if both exist
            if frontmatter_str and body_prefix:
                new_content = frontmatter_str + "\n" + body_prefix + original_body
            else:
                new_content = frontmatter_str + body_prefix + original_body

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
