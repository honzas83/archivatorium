import logging
import re
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

from ocrpolish.data_model import (
    TAG_PREFIX_ENTITY,
    TAG_PREFIX_TAG,
    TAG_PREFIX_TOPIC,
)
from ocrpolish.models.metadata import CanonicalTags, LastDateSchema, MetadataSchema
from ocrpolish.services.ollama_client import OllamaClient
from ocrpolish.services.tagging_service import TaggingService
from ocrpolish.utils.metadata import (
    extract_last_page_header,
    flatten_metadata,
    format_as_callout,
    format_hierarchical_tag,
    format_metadata_table,
    generate_citation_callout,
    mirror_file,
    normalize_obsidian_tags,
    parse_frontmatter,
    prefix_tag,
    safe_read_text,
    stringify_frontmatter,
)
from ocrpolish.utils.tag_parser import CanonicalTagParser

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
        tagging_service: TaggingService | None = None,
        input_dir: Path | None = None,
    ):
        self.client = ollama_client
        self.output_dir = output_dir
        self.overwrite = overwrite
        self.vault_root = vault_root
        self.pdf_dir = pdf_dir
        self.tagging_service = tagging_service
        self.input_dir = input_dir
        self.conceptual_tag_counts: Counter[str] = Counter()
        self.topic_counts: Counter[str] = Counter()
        self.entity_counts: dict[str, Counter[str]] = {
            "State": Counter(),
            "Org": Counter(),
            "City": Counter(),
            "Person": Counter(),
        }
        self.scanned_files_tags: dict[Path, CanonicalTags] = {}

    def _get_pdf_link(self, input_file: Path) -> str:
        """Calculates the Obsidian-style link to the source PDF."""
        pdf_filename = f"{input_file.stem}.pdf"

        # If we are mirroring (indicated by input_dir being set),
        # we assume PDFs are in a 'pdf/' subdirectory relative to the MD.
        if self.input_dir and not self.vault_root and not self.pdf_dir:
            return f"[[pdf/{pdf_filename}]]"

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
        # 1. Clean dict and handle renames
        clean_dict: dict[str, Any] = {}
        for k, v in raw_dict.items():
            new_key = k.removeprefix("correspondence_")
            # Rename legacy fields to intent if found
            if new_key in ("transaction", "correspondence"):
                new_key = "intent"
            clean_dict[new_key] = v
        raw_dict = clean_dict

        # 2. Standardize tags (flat tags)
        if raw_dict.get("tags"):
            raw_dict["tags"] = normalize_obsidian_tags(raw_dict["tags"])

        # 3. Add source PDF link
        raw_dict["source"] = self._get_pdf_link(input_file)

        # 4. Define primary field order and extract them
        primary_keys = [
            "title",
            "summary",
            "pages",
            "sender",
            "recipient",
            "intent",
            "author_name",
            "author_institution",
            "date",
            "archive_code",
            "language",
            "location_city",
            "location_state",
            "source",
        ]

        # 5. Exclude mentioned_* from frontmatter (they go to Callout)
        excluded_keys = ["mentioned_states", "mentioned_organisations", "mentioned_cities"]

        metadata_dict = {}
        for k in primary_keys:
            if k in raw_dict:
                val = raw_dict.pop(k)
                # Only add if value is not "empty"
                if val not in (None, "", [], {}):
                    metadata_dict[k] = val

        # 6. Flatten the remaining fields and filter them
        flattened_remainder = flatten_metadata(raw_dict)
        for k, v in flattened_remainder.items():
            # Ensure excluded keys don't sneak back in after flattening
            if k not in excluded_keys and v not in (None, "", [], {}):
                metadata_dict[k] = v
        return metadata_dict

    def _normalize_topic_citations(self, text: str) -> str:
        """
        Normalizes citations in text: replacements of 'quote' or "quote" with _"quote"_.
        Avoids matching single quotes used as apostrophes by checking word boundaries.
        """
        if not text:
            return ""
        # Replace single or double quotes with italicized double quotes,
        # ensuring the closing quote matches the opening one and is not followed by a word character.
        return re.sub(r"(?<!\w)(['\"])(.*?)\1(?!\w)", r'_"\2"_', text)

    def process_file(
        self, input_file: Path, output_file: Path, frequent_tags: list[str] | None = None
    ) -> bool:
        """
        Processes a single file: extracts metadata and writes to output.
        """
        if output_file.exists() and not self.overwrite:
            logger.debug(f"Skipping {input_file} (output already exists)")
            return False

        try:
            content = safe_read_text(input_file)

            # 1. Separate existing frontmatter from body
            existing_metadata, original_body = parse_frontmatter(content)

            # Prepare tag and entity context if available
            tag_context = ""
            if frequent_tags:
                tag_context = (
                    f"\nIMPORTANT: Prioritize using these existing tags for consistency: "
                    f"{', '.join(frequent_tags)}. "
                    "Only create new tags if the current list is not sufficient."
                )

            entity_context = ""
            top_states = [s for s, _ in self.entity_counts["State"].most_common(20)]
            top_orgs = [o for o, _ in self.entity_counts["Org"].most_common(20)]
            top_cities = [c for c, _ in self.entity_counts["City"].most_common(20)]

            if top_states or top_orgs or top_cities:
                entity_context = (
                    "\nIMPORTANT: Prioritize using these existing entities for consistency:\n"
                )
                if top_states:
                    entity_context += f"- States: {', '.join(top_states)}\n"
                if top_orgs:
                    entity_context += f"- Organisations: {', '.join(top_orgs)}\n"
                if top_cities:
                    entity_context += f"- Cities: {', '.join(top_cities)}\n"

            # Phase 1: Primary Extraction (First chunk)
            first_chunk = content[:CHUNK_SIZE]
            prompt = (
                f"Source Filename: {input_file.name}\n\n"
                f"Document Content (First Part):\n\n{first_chunk}\n\n"
                "Please extract metadata following these strict rules:\n"
                "1. 'title' must be extracted carefully in its ORIGINAL LANGUAGE. "
                "DO NOT use ALL UPPERCASE even if the source text does. You MUST use natural "
                "casing appropriate for the language: for English titles, use Title Case "
                "(e.g., 'Summary Record of a Meeting'); for French titles, use Sentence case "
                "(e.g., 'Compte rendu sommaire d'une réunion'). It is usually on the first "
                "page, but could also be part of the second page. The title should make "
                "sense in the context of the summary and abstract.\n"
                "2. 'summary' must be exactly one sentence. It must be an independent entity.\n"
                "3. 'abstract' must be a detailed overview, limited to at most 20 sentences. "
                "It must be a superset of the summary.\n"
                "4. 'mentioned_states' must only contain full names of nation states.\n"
                "5. 'mentioned_organisations' should include international bodies.\n"
                "6. 'mentioned_cities' MUST be a list of strings in 'City, State' format "
                "(e.g., ['London, United Kingdom', 'Washington, United States']).\n"
                "7. 'date' must be the complete official document date (YYYY-MM-DD).\n"
                "8. 'archive_code' should be derived using both the text and the filename.\n"
                "9. If the document is a letter, describe 'sender', 'recipient', "
                "and 'intent' (the specific action/request).\n"
                "10. 'references' should contain a list of any other reference codes.\n"
                "11. IMPORTANT: Use English for all metadata values EXCEPT 'title', "
                "which must remain in the original language.\n"
                "12. IMPORTANT: Convert certain fields to Title Case if found in ALL CAPS. "
                "Preserve uppercase for acronyms.\n"
                "13. Ensure 'location_state' is filled if 'location_city' is identified.\n"
                "14. Generate between 3 and 8 'tags'. No spaces.\n"
                "15. Interpret and correct OCR errors using context."
                f"{tag_context}"
                f"{entity_context}"
            )

            metadata_obj = self.client.extract_structured(prompt, MetadataSchema)

            # Counters are updated downstream after the output file is written.

            # Convert to dict.
            raw_dict = metadata_obj.model_dump()

            # US-014: Extract page count from source headers
            pages = extract_last_page_header(content)
            if pages:
                raw_dict["pages"] = pages

            # Phase 2: Secondary Pass for Date (only if missing and document is large)
            if not raw_dict.get("date") and len(content) > LARGE_DOC_THRESHOLD:
                logger.debug(f"Date missing from first chunk of {input_file.name}. Scanning end...")
                last_chunk = content[-CHUNK_SIZE:]
                date_prompt = (
                    f"Document Content (Final Part):\n\n{last_chunk}\n\n"
                    "Extract ONLY the complete official date (YYYY-MM-DD)."
                )
                try:
                    date_obj = self.client.extract_structured(date_prompt, LastDateSchema)
                    if date_obj.date:
                        raw_dict["date"] = date_obj.date
                        logger.debug(f"Found date at end of document: {date_obj.date}")
                except Exception as e:
                    logger.warning(f"Secondary date extraction failed: {e}")

            # Prepare metadata for Obsidian (standardization, flattening, prefix removal)
            # We merge with existing metadata here
            combined_raw = {**existing_metadata, **raw_dict}

            # US-014: Extract mentioned entities BEFORE filtering for frontmatter
            states_list = combined_raw.get("mentioned_states", [])
            orgs_list = combined_raw.get("mentioned_organisations", [])
            cities_list = combined_raw.get("mentioned_cities", [])

            metadata_dict = self._prepare_obsidian_metadata(combined_raw, input_file)

            # User Story 2: Move title and abstract to body callout
            # We keep title in frontmatter for searchability (as requested),
            # but move abstract exclusively to the body.
            title = metadata_dict.get("title", "")
            abstract = metadata_dict.pop("abstract", "")

            # Step 2: Precision Tagging Pass
            topic_list_items = []
            entity_tags: list[str] = []
            tag_list_items = []

            if self.tagging_service:
                tagging_result = self.tagging_service.extract_tags(content)
                if tagging_result.topic_tags:
                    for t in tagging_result.topic_tags:
                        norm_reason = self._normalize_topic_citations(t.reason)
                        prefixed_tag = prefix_tag(t.topic, TAG_PREFIX_TOPIC)
                        topic_list_items.append(f"- {prefixed_tag} — {norm_reason}")

                if tagging_result.entity_tags:
                    entity_tags = [
                        prefix_tag(e, TAG_PREFIX_ENTITY) for e in tagging_result.entity_tags
                    ]
                if tagging_result.conceptual_tags:
                    tag_list_items = [
                        prefix_tag(t, TAG_PREFIX_TAG) for t in tagging_result.conceptual_tags
                    ]
            else:
                # Fallback to Step 1 extraction if no tagging service
                state_fallback = states_list[0] if states_list else "Unknown"
                default_state = metadata_dict.get("location_state") or state_fallback
                for s in states_list:
                    entity_tags.append(
                        prefix_tag(format_hierarchical_tag("State", s), TAG_PREFIX_ENTITY)
                    )
                for o in orgs_list:
                    entity_tags.append(
                        prefix_tag(format_hierarchical_tag("Org", o), TAG_PREFIX_ENTITY)
                    )
                for c_item in cities_list:
                    if "," in c_item:
                        city, state = [part.strip() for part in c_item.split(",", 1)]
                    else:
                        city = c_item
                        state = default_state
                    prefixed = prefix_tag(
                        format_hierarchical_tag("City", state, city), TAG_PREFIX_ENTITY
                    )
                    entity_tags.append(prefixed)

                flat_tags = metadata_dict.get("tags", [])
                if flat_tags:
                    tag_list_items = [prefix_tag(t, TAG_PREFIX_TAG) for t in flat_tags]

            # Group entities by type for the callout
            entity_section_body = ""
            if entity_tags:
                # Map internal types to plural display labels
                type_labels = {
                    "City": "Cities",
                    "Org": "Organisations",
                    "Person": "Persons",
                    "State": "States",
                }

                grouped_entities: dict[str, list[str]] = {}
                for e_tag in sorted(entity_tags):
                    tag = f"#{e_tag}" if not e_tag.startswith("#") else e_tag

                    # Extract type: #Prefix/Type/Name -> Type
                    full_tag = tag.lstrip("#")
                    etype = "Other"

                    if TAG_PREFIX_ENTITY:
                        prefix_with_slash = f"{TAG_PREFIX_ENTITY}/"
                        if full_tag.startswith(prefix_with_slash):
                            # Get component after Prefix/
                            sub_tag = full_tag[len(prefix_with_slash) :]
                            parts = sub_tag.split("/", 1)
                            etype = parts[0] if len(parts) > 0 else "Other"
                    else:
                        # No prefix, just Type/Name
                        parts = full_tag.split("/", 1)
                        etype = parts[0] if len(parts) > 1 else "Other"

                    label = type_labels.get(etype, etype)
                    if label not in grouped_entities:
                        grouped_entities[label] = []
                    grouped_entities[label].append(f"  - {tag}")

                # Sort group keys and join with nested structure
                entity_groups = []
                for label in sorted(grouped_entities.keys()):
                    group_lines = [f"* {label}"]
                    group_lines.extend(grouped_entities[label])
                    entity_groups.append("\n".join(group_lines))

                entity_section_body = "\n".join(entity_groups)

            # US3: Remove tags from frontmatter property
            metadata_dict.pop("tags", [])

            # Generate visual metadata table
            # We use metadata_dict because it contains the prepared 'source' link
            # and renamed correspondence fields.
            metadata_table = format_metadata_table(metadata_dict)
            metadata_callout = format_as_callout(
                metadata_table, title="Metadata", callout_type="info"
            )

            # Build the callout block with dedicated sections for topics and tags
            body_prefix = ""
            if title or abstract or topic_list_items or tag_list_items or entity_section_body:
                sections = []
                if title:
                    sections.append(f"# {title}")
                if abstract:
                    sections.append(abstract)

                if topic_list_items:
                    topic_section = "## Categories/Topics\n\n" + "\n".join(topic_list_items)
                    sections.append(topic_section)

                if entity_section_body:
                    entity_section = "## Entities\n\n" + entity_section_body
                    sections.append(entity_section)

                if tag_list_items:
                    tag_section = "## Tags\n\n" + " ".join(tag_list_items)
                    sections.append(tag_section)

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
            new_content = frontmatter_str
            if metadata_callout:
                new_content += "\n" + metadata_callout
            if body_prefix:
                new_content += "\n" + body_prefix

            new_content += "\n" + original_body

            # Append citation callout at the end
            combined_raw["url_date"] = date.today().strftime("%Y-%m-%d")
            citation_callout = generate_citation_callout(combined_raw)

            if not new_content.endswith("\n\n"):
                if not new_content.endswith("\n"):
                    new_content += "\n\n"
                else:
                    new_content += "\n"

            new_content += citation_callout

            # Ensure output is .md (Task T010)
            output_file = output_file.with_suffix(".md")
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(new_content, encoding="utf-8")
            self._update_file_counters(output_file, new_content)
            return True
        except Exception as e:
            logger.error(f"Error processing {input_file}: {e}")
            return False

    def get_files(
        self, input_dir: Path, mask: str = "*.md", recursive: bool = True, all_files: bool = False
    ) -> list[Path]:
        """
        Returns a list of files to be processed.
        If all_files is True, returns all files for mirroring.
        Otherwise returns only files matching the mask, excluding sidecar .filtered.md files.
        """
        if all_files:
            pattern = "**/*" if recursive else "*"
            return [f for f in input_dir.glob(pattern) if f.is_file()]

        pattern = f"**/{mask}" if recursive else mask
        all_files_list = input_dir.glob(pattern)
        return [f for f in all_files_list if not f.name.endswith(".filtered.md")]

    def process_directory(
        self, input_dir: Path, mask: str = "*.md", recursive: bool = True
    ) -> None:
        """
        Traverses directory and processes all files.
        Markdown files are enriched, others are mirrored via hardlink.
        """
        self.preflight_scan()
        files = sorted(self.get_files(input_dir, mask=mask, recursive=recursive, all_files=True))
        logger.info(f"Found {len(files)} files to process in {input_dir}")

        for input_file in files:
            relative_path = input_file.relative_to(input_dir)
            output_file = self.output_dir / relative_path

            if input_file.suffix.lower() == ".md" and not input_file.name.endswith(".filtered.md"):
                # Get 50 most frequent tags
                frequent_tags = [tag for tag, _ in self.conceptual_tag_counts.most_common(50)]
                self.process_file(input_file, output_file, frequent_tags)
            elif input_file.suffix.lower() == ".pdf":
                # Mirror PDFs to 'pdf' subdirectory
                pdf_output_file = output_file.parent / "pdf" / output_file.name
                mirror_file(input_file, pdf_output_file)
            else:
                # Mirror other non-markdown files (or filtered md files)
                mirror_file(input_file, output_file)

    def preflight_scan(self) -> None:
        """Scans the output directory and populates the registry and global counters with existing tags."""
        self.scanned_files_tags.clear()
        self.conceptual_tag_counts = Counter()
        self.topic_counts = Counter()
        self.entity_counts = {
            "State": Counter(),
            "Org": Counter(),
            "City": Counter(),
            "Person": Counter(),
        }

        if not self.output_dir.exists():
            return

        parser = CanonicalTagParser()
        for md_file in self.output_dir.rglob("*.md"):
            if md_file.is_file() and not md_file.name.endswith(".filtered.md"):
                try:
                    content = safe_read_text(md_file)
                    tags = parser.parse_text(content, file_path=md_file)
                    self.scanned_files_tags[md_file] = tags
                    self._add_tags_to_counters(tags)
                except Exception as e:
                    logger.warning(
                        f"Failed to parse existing file {md_file} during preflight scan: {e}"
                    )

    def _add_tags_to_counters(self, tags: CanonicalTags) -> None:
        if tags.conceptual_tags:
            self.conceptual_tag_counts.update(tags.conceptual_tags)
        if tags.topics:
            self.topic_counts.update(tags.topics)
        for etype, values in tags.entities.items():
            if etype in self.entity_counts and values:
                self.entity_counts[etype].update(values)

    def _subtract_tags_from_counters(self, tags: CanonicalTags) -> None:
        if tags.conceptual_tags:
            self.conceptual_tag_counts.subtract(tags.conceptual_tags)
        if tags.topics:
            self.topic_counts.subtract(tags.topics)
        for etype, values in tags.entities.items():
            if etype in self.entity_counts and values:
                self.entity_counts[etype].subtract(values)

    def _update_file_counters(self, file_path: Path, new_content: str) -> None:
        """Subtracts old tags for a file and adds new tags to the global counters."""
        if file_path in self.scanned_files_tags:
            old_tags = self.scanned_files_tags[file_path]
            self._subtract_tags_from_counters(old_tags)

        parser = CanonicalTagParser()
        new_tags = parser.parse_text(new_content, file_path=file_path)
        self._add_tags_to_counters(new_tags)
        self.scanned_files_tags[file_path] = new_tags
