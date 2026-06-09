import logging
import re
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from ocrpolish.data_model import (
    TAG_PREFIX_ENTITY,
    TAG_PREFIX_TAG,
    TAG_PREFIX_TOPIC,
)
from ocrpolish.models.metadata import (
    AggregatedTaggingResult,
    CanonicalTags,
    LastDateSchema,
    MetadataSchema,
)
from ocrpolish.services.ollama_client import OllamaClient
from ocrpolish.services.tagging_service import TaggingService
from ocrpolish.utils.metadata import (
    extract_last_page_header,
    flatten_metadata,
    format_as_callout,
    format_metadata_table,
    generate_citation_callout,
    generate_citekey,
    is_generated_document_markdown,
    mirror_file,
    parse_frontmatter,
    prefix_tag,
    reconcile_metadata,
    safe_read_text,
    stringify_frontmatter,
    strip_generated_sections,
)
from ocrpolish.utils.tag_parser import CanonicalTagParser

logger = logging.getLogger(__name__)

# Constants for context window management
CHUNK_SIZE = 10000
LARGE_DOC_THRESHOLD = 12000


@dataclass(frozen=True)
class ParsedSource:
    raw_content: str
    cleaned_content: str
    existing_metadata: dict[str, Any]


@dataclass(frozen=True)
class ExtractedMetadata:
    raw_dict: dict[str, Any]


@dataclass(frozen=True)
class GeneratedTagSections:
    topic_items: list[str]
    entity_tags: list[str]
    conceptual_tags: list[str]
    entity_section_body: str


@dataclass(frozen=True)
class FrontmatterStage:
    metadata: dict[str, Any]
    frontmatter: str
    title: str
    abstract: str


@dataclass(frozen=True)
class CalloutStage:
    metadata_callout: str
    body_prefix: str
    citation_callout: str
    original_body: str


@dataclass(frozen=True)
class TaggingReuseHints:
    preferred_conceptual_tags: list[str]
    preferred_entities: dict[str, list[str]]
    preferred_topics: list[str]


class MetadataProcessor:
    def __init__(  # noqa: PLR0913
        self,
        ollama_client: OllamaClient,
        output_dir: Path,
        overwrite: bool = False,
        vault_root: Path | None = None,
        pdf_dir: Path | None = None,
        tagging_service: TaggingService | None = None,
        input_dir: Path | None = None,
        citekey_mode: str = "stem",
    ):
        self.client = ollama_client
        self.output_dir = output_dir
        self.overwrite = overwrite
        self.vault_root = vault_root
        self.pdf_dir = pdf_dir
        self.tagging_service = tagging_service
        self.input_dir = input_dir
        self.citekey_mode = citekey_mode
        self.conceptual_tag_counts: Counter[str] = Counter()
        self.topic_counts: Counter[str] = Counter()
        self.entity_counts: dict[str, Counter[str]] = {
            "State": Counter(),
            "Org": Counter(),
            "City": Counter(),
            "Person": Counter(),
        }
        self.scanned_files_tags: dict[Path, CanonicalTags] = {}
        self._preflight_done = False

    def get_mirrored_pdf_path(self, input_file: Path) -> Path:
        """Return the generated vault location for a source PDF beside its Markdown."""
        relative_parent = Path()
        if self.input_dir:
            try:
                relative_parent = input_file.relative_to(self.input_dir).parent
            except ValueError:
                relative_parent = Path()
        return self.output_dir / relative_parent / "pdf" / f"{input_file.stem}.pdf"

    def _get_pdf_link(self, input_file: Path) -> str:
        """Calculates the Obsidian-style link to the mirrored source PDF."""
        return f"[[pdf/{input_file.stem}.pdf]]"

    def _prepare_obsidian_metadata(
        self, raw_dict: dict[str, Any], input_file: Path, output_file: Path
    ) -> dict[str, Any]:
        """Prepares the metadata dictionary for Obsidian frontmatter and table output."""
        # 1. Clean dict and handle renames
        clean_dict: dict[str, Any] = {}
        for k, v in raw_dict.items():
            new_key = k.removeprefix("correspondence_")
            # Rename legacy fields to intent if found
            if new_key in ("transaction", "correspondence"):
                new_key = "intent"
            # Exclude obsolete fields
            if new_key in (
                "mentioned_states",
                "mentioned_organisations",
                "mentioned_cities",
                "tags",
            ):
                continue
            clean_dict[new_key] = v
        raw_dict = clean_dict

        # 2. Add source PDF link
        raw_dict["source"] = self._get_pdf_link(input_file)

        # 3. Add citekey
        raw_dict["citekey"] = generate_citekey(
            output_file=output_file,
            mode=self.citekey_mode,
            vault_root=self.vault_root,
            output_dir=self.output_dir,
        )

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
            "citekey",
            "language",
            "location_city",
            "location_state",
            "source",
            "references",
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

    def _normalize_topic_citations(self, text: str) -> str:
        """
        Normalizes citations in text: replacements of 'quote' or "quote" with _"quote"_.
        Avoids matching single quotes used as apostrophes by checking word boundaries.
        """
        if not text:
            return ""
        # Replace single or double quotes with italicized double quotes, ensuring
        # the closing quote matches the opening one and is not followed by a word character.
        return re.sub(r"(?<!\w)(['\"])(.*?)\1(?!\w)", r'_"\2"_', text)

    def _skip_existing_output(self, input_file: Path, output_file: Path) -> bool:
        if not output_file.exists() or self.overwrite:
            return False

        logger.debug(f"Skipping {input_file} (output already exists)")
        if output_file not in self.scanned_files_tags:
            try:
                content = safe_read_text(output_file)
                parser = CanonicalTagParser()
                tags = parser.parse_text(content, file_path=output_file)
                self._add_tags_to_counters(tags)
                self.scanned_files_tags[output_file] = tags
            except Exception as e:
                logger.warning(
                    f"Failed to parse existing file {output_file} during skip logic: {e}"
                )
        return True

    def _read_source(self, input_file: Path) -> str:
        return safe_read_text(input_file)

    def _parse_source_and_strip_generated_sections(self, raw_content: str) -> ParsedSource:
        existing_metadata, _ = parse_frontmatter(raw_content)
        return ParsedSource(
            raw_content=raw_content,
            cleaned_content=strip_generated_sections(raw_content),
            existing_metadata=existing_metadata,
        )

    def _metadata_context(self, frequent_tags: list[str] | None) -> str:
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

        return f"{tag_context}{entity_context}"

    def _build_metadata_prompt(
        self, input_file: Path, cleaned_content: str, frequent_tags: list[str] | None
    ) -> str:
        first_chunk = cleaned_content[:CHUNK_SIZE]
        return (
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
            "4. 'date' must be the complete official document date (YYYY-MM-DD).\n"
            "5. 'archive_code' should be derived using both the text and the filename.\n"
            "6. If the document is a letter, describe 'sender', 'recipient', "
            "and 'intent' (the specific action/request).\n"
            "7. 'references' should contain a list of any other reference codes.\n"
            "8. IMPORTANT: Use English for all metadata values EXCEPT 'title', "
            "which must remain in the original language.\n"
            "9. IMPORTANT: Convert certain fields to Title Case if found in ALL CAPS. "
            "Preserve uppercase for acronyms.\n"
            "10. Ensure 'location_state' is filled if 'location_city' is identified.\n"
            "11. Interpret and correct OCR errors using context."
            f"{self._metadata_context(frequent_tags)}"
        )

    def _extract_document_metadata(
        self, input_file: Path, cleaned_content: str, frequent_tags: list[str] | None = None
    ) -> ExtractedMetadata:
        prompt = self._build_metadata_prompt(input_file, cleaned_content, frequent_tags)
        metadata_obj = self.client.extract_structured(prompt, MetadataSchema)
        raw_dict = metadata_obj.model_dump()

        pages = extract_last_page_header(cleaned_content)
        if pages:
            raw_dict["pages"] = pages

        if not raw_dict.get("date") and len(cleaned_content) > LARGE_DOC_THRESHOLD:
            logger.debug(f"Date missing from first chunk of {input_file.name}. Scanning end...")
            last_chunk = cleaned_content[-CHUNK_SIZE:]
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

        return ExtractedMetadata(raw_dict=raw_dict)

    def _extract_generated_tags(self, cleaned_content: str) -> GeneratedTagSections:
        result = AggregatedTaggingResult()
        if self.tagging_service:
            result = self.tagging_service.extract_tags(
                cleaned_content,
                reuse_hints=self._build_tagging_reuse_hints(),
            )
        return self._format_generated_tags(result)

    def _build_tagging_reuse_hints(self) -> TaggingReuseHints:
        return TaggingReuseHints(
            preferred_conceptual_tags=[
                tag for tag, _ in self.conceptual_tag_counts.most_common(50)
            ],
            preferred_entities={
                etype: [value for value, _ in counter.most_common(20)]
                for etype, counter in self.entity_counts.items()
            },
            preferred_topics=[topic for topic, _ in self.topic_counts.most_common(20)],
        )

    def _format_generated_tags(
        self, tagging_result: AggregatedTaggingResult
    ) -> GeneratedTagSections:
        topic_items = []
        if tagging_result.topic_tags:
            for topic in tagging_result.topic_tags:
                norm_reason = self._normalize_topic_citations(topic.reason)
                prefixed_tag = prefix_tag(topic.topic, TAG_PREFIX_TOPIC)
                topic_items.append(f"- {prefixed_tag} — {norm_reason}")

        entity_tags = [prefix_tag(e, TAG_PREFIX_ENTITY) for e in tagging_result.entity_tags]
        conceptual_tags = [prefix_tag(t, TAG_PREFIX_TAG) for t in tagging_result.conceptual_tags]

        return GeneratedTagSections(
            topic_items=topic_items,
            entity_tags=entity_tags,
            conceptual_tags=conceptual_tags,
            entity_section_body=self._build_entity_section(entity_tags),
        )

    def _build_entity_section(self, entity_tags: list[str]) -> str:
        if not entity_tags:
            return ""

        type_labels = {
            "City": "Cities",
            "Org": "Organisations",
            "Person": "Persons",
            "State": "States",
        }
        grouped_entities: dict[str, list[str]] = {}
        for entity_tag in sorted(entity_tags):
            tag = f"#{entity_tag}" if not entity_tag.startswith("#") else entity_tag
            full_tag = tag.lstrip("#")
            etype = "Other"

            if TAG_PREFIX_ENTITY:
                prefix_with_slash = f"{TAG_PREFIX_ENTITY}/"
                if full_tag.startswith(prefix_with_slash):
                    sub_tag = full_tag[len(prefix_with_slash) :]
                    parts = sub_tag.split("/", 1)
                    etype = parts[0] if parts else "Other"
            else:
                parts = full_tag.split("/", 1)
                etype = parts[0] if len(parts) > 1 else "Other"

            label = type_labels.get(etype, etype)
            grouped_entities.setdefault(label, []).append(f"  - {tag}")

        entity_groups = []
        for label in sorted(grouped_entities.keys()):
            group_lines = [f"* {label}"]
            group_lines.extend(grouped_entities[label])
            entity_groups.append("\n".join(group_lines))
        return "\n".join(entity_groups)

    def _reconcile_metadata_and_tags(
        self,
        existing_metadata: dict[str, Any],
        extracted_metadata: ExtractedMetadata,
        input_file: Path,
        output_file: Path,
    ) -> dict[str, Any]:
        raw_dict = dict(extracted_metadata.raw_dict)
        raw_dict["source"] = self._get_pdf_link(input_file)
        raw_dict["citekey"] = generate_citekey(
            output_file=output_file,
            mode=self.citekey_mode,
            vault_root=self.vault_root,
            output_dir=self.output_dir,
        )
        reconciled_raw = reconcile_metadata(existing_metadata, raw_dict)
        return self._prepare_obsidian_metadata(reconciled_raw, input_file, output_file)

    def _render_frontmatter(self, metadata_dict: dict[str, Any]) -> FrontmatterStage:
        metadata = dict(metadata_dict)
        title = metadata.get("title", "")
        abstract = metadata.pop("abstract", "")
        metadata.pop("tags", [])
        return FrontmatterStage(
            metadata=metadata,
            frontmatter=stringify_frontmatter(metadata),
            title=title,
            abstract=abstract,
        )

    def _render_callouts(
        self, frontmatter: FrontmatterStage, tag_sections: GeneratedTagSections, original_body: str
    ) -> CalloutStage:
        metadata_table = format_metadata_table(frontmatter.metadata)
        metadata_callout = format_as_callout(metadata_table, title="Metadata", callout_type="info")

        body_prefix = self._render_abstract_callout(frontmatter, tag_sections)
        cleaned_body = self._clean_original_body(original_body, frontmatter.title)

        citation_metadata = dict(frontmatter.metadata)
        citation_metadata["url_date"] = date.today().strftime("%Y-%m-%d")
        citation_callout = generate_citation_callout(citation_metadata)

        return CalloutStage(
            metadata_callout=metadata_callout,
            body_prefix=body_prefix,
            citation_callout=citation_callout,
            original_body=cleaned_body,
        )

    def _render_abstract_callout(
        self, frontmatter: FrontmatterStage, tag_sections: GeneratedTagSections
    ) -> str:
        if not (
            frontmatter.title
            or frontmatter.abstract
            or tag_sections.topic_items
            or tag_sections.conceptual_tags
            or tag_sections.entity_section_body
        ):
            return ""

        sections = []
        if frontmatter.title:
            sections.append(f"# {frontmatter.title}")
        if frontmatter.abstract:
            sections.append(frontmatter.abstract)
        if tag_sections.topic_items:
            sections.append("## Categories/Topics\n\n" + "\n".join(tag_sections.topic_items))
        if tag_sections.entity_section_body:
            sections.append("## Entities\n\n" + tag_sections.entity_section_body)
        if tag_sections.conceptual_tags:
            sections.append("## Tags\n\n" + " ".join(tag_sections.conceptual_tags))

        return format_as_callout("\n\n".join(sections).strip(), title="", callout_type="abstract")

    def _clean_original_body(self, original_body: str, title: str) -> str:
        original_body = original_body.lstrip()
        while True:
            start_len = len(original_body)
            if original_body.startswith("---"):
                original_body = re.sub(r"^---\s*", "", original_body)
            if title:
                escaped_title = re.escape(title)
                original_body = re.sub(
                    rf"^(#+\s+)?{escaped_title}\s*\n?", "", original_body, flags=re.IGNORECASE
                )
            if len(original_body) == start_len:
                break
            original_body = original_body.lstrip()
        return original_body

    def _assemble_output(self, frontmatter: FrontmatterStage, callouts: CalloutStage) -> str:
        new_content = frontmatter.frontmatter
        if callouts.metadata_callout:
            new_content += "\n" + callouts.metadata_callout
        if callouts.body_prefix:
            new_content += "\n" + callouts.body_prefix
        new_content += "\n" + callouts.original_body

        if not new_content.endswith("\n\n"):
            if not new_content.endswith("\n"):
                new_content += "\n\n"
            else:
                new_content += "\n"
        return new_content + callouts.citation_callout

    def _write_output(self, output_file: Path, content: str) -> Path:
        output_file = output_file.with_suffix(".md")
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(content, encoding="utf-8")
        return output_file

    def _ingest_generated_output_tags(self, output_file: Path, content: str) -> None:
        self._update_file_counters(output_file, content)

    def process_file(
        self, input_file: Path, output_file: Path, frequent_tags: list[str] | None = None
    ) -> bool:
        """
        Processes a single file: extracts metadata and writes to output.
        """
        output_file = output_file.with_suffix(".md")
        if self._skip_existing_output(input_file, output_file):
            return False

        try:
            raw_content = self._read_source(input_file)
            parsed = self._parse_source_and_strip_generated_sections(raw_content)
            extracted = self._extract_document_metadata(
                input_file, parsed.cleaned_content, frequent_tags
            )
            tag_sections = self._extract_generated_tags(parsed.cleaned_content)
            metadata = self._reconcile_metadata_and_tags(
                parsed.existing_metadata, extracted, input_file, output_file
            )
            frontmatter = self._render_frontmatter(metadata)
            callouts = self._render_callouts(frontmatter, tag_sections, parsed.cleaned_content)
            new_content = self._assemble_output(frontmatter, callouts)
            written_file = self._write_output(output_file, new_content)
            self._ingest_generated_output_tags(written_file, new_content)
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
                pdf_output_file = self.get_mirrored_pdf_path(input_file)
                if pdf_output_file.exists() and not pdf_output_file.samefile(input_file):
                    raise ValueError(
                        f"Ambiguous mirrored PDF target already exists: {pdf_output_file}"
                    )
                mirror_file(input_file, pdf_output_file)
            else:
                # Mirror other non-markdown files (or filtered md files)
                mirror_file(input_file, output_file)

    def preflight_scan(self) -> None:
        """Scan output once and populate the registry and global counters with existing tags."""
        if self._preflight_done:
            return
        self._preflight_done = True
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
            if not md_file.is_file() or not is_generated_document_markdown(
                md_file, vault_root=self.output_dir
            ):
                continue
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
