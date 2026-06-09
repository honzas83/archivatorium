import logging
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import xlsxwriter  # type: ignore
import yaml

from ocrpolish.models.metadata import CanonicalTags
from ocrpolish.utils.metadata import parse_frontmatter, safe_identifier
from ocrpolish.utils.nlp import normalize_tag_component
from ocrpolish.utils.tag_parser import CanonicalTagParser

logger = logging.getLogger(__name__)


@dataclass
class EntityReference:
    prefix: str
    value: str
    label: str


@dataclass
class IndexEntry:
    doc_path: Path
    title: str = ""
    summary: str = ""
    date: str = ""
    entities: list[EntityReference] = field(default_factory=list)
    raw_metadata: dict[str, Any] = field(default_factory=dict)
    canonical_tags: CanonicalTags = field(default_factory=CanonicalTags)


class IndexingService:
    def __init__(self, input_dir: Path, topics_yaml: Path | None = None):
        self.input_dir = input_dir
        self.topics_yaml = topics_yaml
        self.entries: list[IndexEntry] = []

    def process_file(self, file_path: Path) -> None:
        """Processes a single markdown file and extracts its metadata for backward compatibility."""
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return

        try:
            metadata, body = parse_frontmatter(content)
        except Exception as e:
            logger.warning(f"Malformed frontmatter in {file_path}: {e}")
            metadata = {}

        parser = CanonicalTagParser()
        canonical_tags = parser.parse_text(content, file_path=file_path)

        entities = []
        for p in canonical_tags.raw_paths:
            if p.startswith("Entities/"):
                parts = p.split("/")
                if len(parts) >= 2:
                    etype = parts[1]
                    label = parts[-1].replace("-", " ")
                    tag = f"#{p}"
                    entities.append(EntityReference(prefix=etype, value=tag, label=label))

        entry = IndexEntry(
            doc_path=file_path.relative_to(self.input_dir),
            title=metadata.get("title", file_path.stem),
            summary=metadata.get("summary", ""),
            date=metadata.get("date", ""),
            entities=entities,
            raw_metadata=metadata,
            canonical_tags=canonical_tags,
        )
        self.entries.append(entry)

    def generate_xlsx(self, output_path: Path) -> None:
        """Generates an XLSX file containing pivoted canonical tags and core metadata."""
        if not self.entries:
            logger.warning("No entries to export to XLSX.")
            return

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        workbook = xlsxwriter.Workbook(str(output_path))
        sheet = workbook.add_worksheet("Metadata Index")

        core_fields = [
            "File Path",
            "Citekey",
            "Title",
            "Summary",
            "Date",
            "Archive Code",
            "Language",
            "Location City",
            "Location State",
            "Sender",
            "Recipient",
            "Intent",
            "References",
        ]
        tag_fields = [
            "conceptual_tags",
            "topic_tags",
            "state_entities",
            "org_entities",
            "city_entities",
            "person_entities",
        ]
        headers = core_fields + tag_fields

        bold = workbook.add_format({"bold": True})
        for col_num, header in enumerate(headers):
            sheet.write(0, col_num, header, bold)

        for row_num, entry in enumerate(self.entries, start=1):
            citekey = entry.raw_metadata.get("citekey")
            if not citekey:
                citekey = safe_identifier(entry.doc_path.stem)

            refs_val = entry.raw_metadata.get("references", "")
            if isinstance(refs_val, list):
                refs_val = ", ".join(map(str, refs_val))

            core_vals = {
                "File Path": str(entry.doc_path),
                "Citekey": citekey,
                "Title": entry.title,
                "Summary": entry.summary,
                "Date": entry.date,
                "Archive Code": entry.raw_metadata.get("archive_code", ""),
                "Language": entry.raw_metadata.get("language", "English"),
                "Location City": entry.raw_metadata.get("location_city", ""),
                "Location State": entry.raw_metadata.get("location_state", ""),
                "Sender": entry.raw_metadata.get("sender", ""),
                "Recipient": entry.raw_metadata.get("recipient", ""),
                "Intent": entry.raw_metadata.get("intent", ""),
                "References": refs_val,
            }

            raw_paths = entry.canonical_tags.raw_paths
            # Fallback for XLSX export if canonical tags are empty but entities is populated
            if not raw_paths:
                raw_paths = set()
                for ent in entry.entities:
                    clean = ent.value.lstrip("#")
                    if (
                        clean.startswith("Entities/")
                        or clean.startswith("Topics/")
                        or clean.startswith("Tags/")
                    ):
                        raw_paths.add(clean)
                    # Map old unprefixed tags
                    elif ent.prefix in {"State", "Org", "Person"}:
                        raw_paths.add(f"Entities/{ent.prefix}/{clean.split('/')[-1]}")
                    elif ent.prefix == "City":
                        parts = clean.split("/")
                        if len(parts) >= 2:
                            raw_paths.add(f"Entities/City/{parts[-2]}/{parts[-1]}")
                        else:
                            raw_paths.add(f"Entities/City/Unknown/{clean}")
                    elif ent.prefix == "Category":
                        raw_paths.add(f"Topics/{'/'.join(clean.split('/')[1:])}")

            tag_vals = {
                "conceptual_tags": ", ".join(
                    sorted([f"#{p}" for p in raw_paths if p.startswith("Tags/")])
                ),
                "topic_tags": ", ".join(
                    sorted([f"#{p}" for p in raw_paths if p.startswith("Topics/")])
                ),
                "state_entities": ", ".join(
                    sorted([f"#{p}" for p in raw_paths if p.startswith("Entities/State/")])
                ),
                "org_entities": ", ".join(
                    sorted([f"#{p}" for p in raw_paths if p.startswith("Entities/Org/")])
                ),
                "city_entities": ", ".join(
                    sorted([f"#{p}" for p in raw_paths if p.startswith("Entities/City/")])
                ),
                "person_entities": ", ".join(
                    sorted([f"#{p}" for p in raw_paths if p.startswith("Entities/Person/")])
                ),
            }

            col_num = 0
            for field_name in core_fields:
                sheet.write(row_num, col_num, str(core_vals.get(field_name, "")))
                col_num += 1

            for field_name in tag_fields:
                sheet.write(row_num, col_num, tag_vals.get(field_name, ""))
                col_num += 1

        sheet.set_column(0, 0, 30)
        sheet.set_column(1, len(headers) - 1, 20)
        workbook.close()
        logger.info(f"Generated XLSX index at {output_path}")

    def generate_markdown_indices(self) -> None:
        """Generates all authoritative Markdown index pages."""
        if not self.entries:
            logger.warning("No entries to index.")
            return

        self._gen_alphabetical_index("Index - States.md", "States", "Entities/State/")
        self._gen_cities_index()
        self._gen_alphabetical_index("Index - Organizations.md", "Organizations", "Entities/Org/")
        self._gen_alphabetical_index("Index - People.md", "People", "Entities/Person/")

        # If topics_yaml exists, use the descriptive formatter for Topics. Otherwise, use alphabetical index.
        if self.topics_yaml and self.topics_yaml.exists():
            self._gen_topics_index_yaml()
        else:
            self._gen_alphabetical_index("Index - Topics.md", "Topics", "Topics/")

        self._gen_alphabetical_index("Index - Tags.md", "Tags", "Tags/")

    def _gen_alphabetical_index(self, filename: str, title: str, prefix: str) -> None:
        """Helper to generate alphabetical grouped indices with document links."""
        tag_to_entries = defaultdict(list)
        for entry in self.entries:
            has_canonical = False
            for p in entry.canonical_tags.raw_paths:
                if p.startswith(prefix):
                    tag = f"#{p}"
                    tag_to_entries[tag].append(entry)
                    has_canonical = True

            if not has_canonical:
                for entity in entry.entities:
                    clean_prefix = prefix.strip("/").split("/")[-1]
                    if entity.prefix == clean_prefix:
                        val = entity.value
                        if not val.startswith("#" + prefix):
                            val = "#" + prefix + val.lstrip("#").split("/")[-1]
                        tag_to_entries[val].append(entry)

        if not tag_to_entries:
            return

        # Sort tags alphabetically
        sorted_tags = sorted(tag_to_entries.keys(), key=lambda t: t.lower())

        lines = [f"# Index of {title}\n"]
        current_letter = ""
        for tag in sorted_tags:
            label = tag.split("/")[-1]
            if not label:
                continue
            letter = label[0].upper()
            if letter != current_letter:
                current_letter = letter
                lines.append(f"## {current_letter}")

            lines.append(f"### {tag}")
            sorted_docs = sorted(tag_to_entries[tag], key=lambda e: str(e.doc_path).lower())
            for doc in sorted_docs:
                title_text = doc.title or doc.doc_path.stem
                lines.append(f"- [[{doc.doc_path}|{title_text}]]")

        self._write_index(filename, "\n".join(lines))

    def _gen_cities_index(self) -> None:
        """Generates Index - Cities.md grouped by state, then city."""
        state_to_cities: dict[str, dict[str, list[IndexEntry]]] = defaultdict(
            lambda: defaultdict(list)
        )
        for entry in self.entries:
            has_canonical = False
            for p in entry.canonical_tags.raw_paths:
                if p.startswith("Entities/City/"):
                    parts = p.split("/")
                    if len(parts) >= 4:
                        state = parts[2]
                        state_display = state.replace("-", " ")
                        tag = f"#{p}"
                        state_to_cities[state_display][tag].append(entry)
                        has_canonical = True

            if not has_canonical:
                for entity in entry.entities:
                    if entity.prefix == "City":
                        parts = entity.value.lstrip("#").split("/")
                        if len(parts) >= 3:
                            state = parts[-2]
                            city = parts[-1]
                            state_display = state.replace("-", " ")
                            tag = f"#Entities/City/{state}/{city}"
                            state_to_cities[state_display][tag].append(entry)

        if not state_to_cities:
            return

        lines = ["# Index of Cities\n"]
        for state_display in sorted(state_to_cities.keys(), key=lambda s: s.lower()):
            lines.append(f"## {state_display}")
            sorted_city_tags = sorted(
                state_to_cities[state_display].keys(), key=lambda t: t.lower()
            )
            for tag in sorted_city_tags:
                lines.append(f"### {tag}")
                sorted_docs = sorted(
                    state_to_cities[state_display][tag], key=lambda e: str(e.doc_path).lower()
                )
                for doc in sorted_docs:
                    title_text = doc.title or doc.doc_path.stem
                    lines.append(f"- [[{doc.doc_path}|{title_text}]]")

        self._write_index("Index - Cities.md", "\n".join(lines))

    def _gen_topics_index_yaml(self) -> None:
        """Generates Index - Topics.md using hierarchical hashtags and YAML descriptions."""
        if not self.topics_yaml or not self.topics_yaml.exists():
            return

        try:
            with open(self.topics_yaml, encoding="utf-8") as f:
                themes_data = yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to parse topics YAML: {e}")
            return

        # Get used topics from both canonical tags and entry.entities
        used_topics = set()
        for entry in self.entries:
            # 1. From canonical tags
            for p in entry.canonical_tags.raw_paths:
                if p.startswith("Topics/"):
                    used_topics.add(f"#{p}")
                    parts = p.split("/")
                    if len(parts) >= 2:
                        used_topics.add(f"#{'/'.join(parts[1:])}")
            # 2. From entities (for backward compatibility)
            for entity in entry.entities:
                used_topics.add(entity.value)
                clean = entity.value.lstrip("#")
                if not clean.startswith("Category/") and "/" in clean:
                    used_topics.add(f"#Category/{clean}")

        lines = ["# Index of Categories/Topics\n"]

        if not themes_data or not isinstance(themes_data, dict):
            return

        categories = themes_data.get("categories", [])
        for cat in categories:
            cat_name = cat.get("category")
            if not cat_name:
                continue

            normalized_cat = normalize_tag_component(cat_name)
            cat_tag_new = f"#Category/{normalized_cat}"
            cat_tag_legacy = f"#{normalized_cat}"
            cat_desc = cat.get("description", "")

            topics = cat.get("topics", [])

            # Helper to check if a specific topic tag is used
            def is_topic_used(c_norm: str, t_norm: str) -> bool:
                return (
                    f"#Category/{c_norm}/{t_norm}" in used_topics
                    or f"#{c_norm}/{t_norm}" in used_topics
                    or f"#Topics/{c_norm}/{t_norm}" in used_topics
                )

            # Check if category or any of its subtopics are used
            has_used_st = any(
                is_topic_used(normalized_cat, normalize_tag_component(t.get("topic", "")))
                for t in topics
            )

            if cat_tag_new in used_topics or cat_tag_legacy in used_topics or has_used_st:
                lines.append(f"## {cat_tag_new}")
                if cat_desc:
                    lines.append(cat_desc)

                for topic in topics:
                    st_name = topic.get("topic")
                    st_desc = topic.get("description", "")
                    st_norm = normalize_tag_component(st_name)
                    st_tag_new = f"#Category/{normalized_cat}/{st_norm}"
                    st_tag_legacy = f"#{normalized_cat}/{st_norm}"
                    st_tag_canonical = f"#Topics/{normalized_cat}/{st_norm}"

                    if (
                        st_tag_new in used_topics
                        or st_tag_legacy in used_topics
                        or st_tag_canonical in used_topics
                    ):
                        lines.append(f"{st_tag_new} -- {st_desc}")

        self._write_index("Index - Topics.md", "\n".join(lines))

    def _write_index(self, filename: str, content: str) -> None:
        """Writes index content to a file in the vault root."""
        output_path = self.input_dir / filename
        output_path.write_text(content, encoding="utf-8")
        logger.info(f"Generated index: {filename}")
