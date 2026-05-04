import logging
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import xlsxwriter  # type: ignore
import yaml  # type: ignore

from ocrpolish.models.metadata import MetadataSchema
from ocrpolish.utils.metadata import extract_abstract_tags, parse_frontmatter

logger = logging.getLogger(__name__)

# Predefined prefixes for indexing (FR-012)
INDEX_PREFIXES = ["State", "City", "Org", "Category"]
# Minimum components for a hierarchical City tag (#City/State/City)
CITY_TAG_MIN_PARTS = 3

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

class IndexingService:
    def __init__(self, input_dir: Path, topics_yaml: Path | None = None):
        self.input_dir = input_dir
        self.topics_yaml = topics_yaml
        self.entries: list[IndexEntry] = []

    def _parse_entity(self, tag: str) -> EntityReference | None:
        """Parses a hierarchical tag into an EntityReference."""
        # Remove # and split by /
        clean_tag = tag.lstrip("#")
        parts = clean_tag.split("/")
        if not parts:
            return None

        prefix = parts[0]
        if prefix not in INDEX_PREFIXES:
            return None

        if len(parts) < 2:  # Must have at least prefix/label
            return None

        # Value is the full tag (with #), label is the last component
        label = parts[-1].replace("-", " ")
        return EntityReference(prefix=prefix, value=tag, label=label)

    def process_file(self, file_path: Path) -> None:
        """Processes a single markdown file and extracts its metadata."""
        try:
            # T025: Handle invalid UTF-8 by replacing characters
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return

        try:
            metadata, body = parse_frontmatter(content)
        except Exception as e:
            # T019: Graceful handling of malformed YAML
            logger.warning(f"Malformed frontmatter in {file_path}: {e}")
            metadata, body = {}, content
        
        raw_tags = metadata.get("tags", [])
        if isinstance(raw_tags, str):
            raw_tags = [raw_tags]
        elif not isinstance(raw_tags, list):
            raw_tags = []
        
        abstract_tags = extract_abstract_tags(body)
        
        all_raw_tags = set()
        for t in raw_tags:
            if not isinstance(t, str):
                continue
            tag = t if t.startswith("#") else f"#{t}"
            all_raw_tags.add(tag)
        all_raw_tags.update(abstract_tags)

        entities = []
        for tag in all_raw_tags:
            entity = self._parse_entity(tag)
            if entity:
                entities.append(entity)

        entry = IndexEntry(
            doc_path=file_path.relative_to(self.input_dir),
            title=metadata.get("title", file_path.stem),
            summary=metadata.get("summary", ""),
            date=metadata.get("date", ""),
            entities=entities,
            raw_metadata=metadata
        )
        self.entries.append(entry)

    def generate_xlsx(self, output_path: Path) -> None:
        """Generates an XLSX file containing all document metadata."""
        if not self.entries:
            logger.warning("No entries to export to XLSX.")
            return

        workbook = xlsxwriter.Workbook(str(output_path))
        sheet = workbook.add_worksheet("Metadata Index")

        schema_fields = MetadataSchema.model_fields.keys()
        headers = ["File Path"] + list(schema_fields)

        bold = workbook.add_format({"bold": True})
        for col_num, header in enumerate(headers):
            sheet.write(0, col_num, header, bold)

        for row_num, entry in enumerate(self.entries, start=1):
            sheet.write(row_num, 0, str(entry.doc_path))
            for col_num, field_name in enumerate(schema_fields, start=1):
                value = entry.raw_metadata.get(field_name, "")
                if isinstance(value, list):
                    value = ", ".join(map(str, value))
                elif value is None:
                    value = ""
                sheet.write(row_num, col_num, str(value))

        sheet.set_column(0, 0, 30)
        sheet.set_column(1, len(headers) - 1, 20)
        workbook.close()
        logger.info(f"Generated XLSX index at {output_path}")

    def _write_index(self, filename: str, content: str) -> None:
        """Writes index content to a file in the vault root."""
        output_path = self.input_dir / filename
        output_path.write_text(content, encoding="utf-8")
        logger.info(f"Generated index: {filename}")

    def generate_markdown_indices(self) -> None:
        """Generates all Markdown index pages."""
        if not self.entries:
            logger.warning("No entries to index.")
            return

        self._gen_states_index()
        self._gen_cities_index()
        self._gen_orgs_index()
        if self.topics_yaml:
            self._gen_topics_index()

    def _gen_states_index(self) -> None:
        """Generates Index - States.md with A-Z grouping."""
        states = set()
        for entry in self.entries:
            for entity in entry.entities:
                if entity.prefix == "State":
                    states.add(entity.value)

        lines = ["# Index of States\n"]
        current_letter = ""
        for tag in sorted(list(states)):
            label = tag.split("/")[-1]
            if not label:
                continue
            letter = label[0].upper()
            if letter != current_letter:
                current_letter = letter
                lines.append(f"## {current_letter}")
            lines.append(tag)

        self._write_index("Index - States.md", "\n".join(lines))

    def _gen_cities_index(self) -> None:
        """Generates Index - Cities.md grouped by state."""
        state_cities = defaultdict(set)
        for entry in self.entries:
            for entity in entry.entities:
                if entity.prefix == "City":
                    parts = entity.value.lstrip("#").split("/")
                    if len(parts) >= CITY_TAG_MIN_PARTS:
                        state = parts[1].replace("-", " ")
                        state_cities[state].add(entity.value)

        lines = ["# Index of Cities\n"]
        for state in sorted(state_cities.keys()):
            lines.append(f"## {state}")
            for city_tag in sorted(list(state_cities[state])):
                lines.append(city_tag)

        self._write_index("Index - Cities.md", "\n".join(lines))

    def _gen_orgs_index(self) -> None:
        """Generates Index - Organizations.md."""
        orgs = set()
        for entry in self.entries:
            for entity in entry.entities:
                if entity.prefix == "Org":
                    orgs.add(entity.value)

        lines = ["# Index of Organizations\n"]
        for tag in sorted(list(orgs)):
            lines.append(tag)

        self._write_index("Index - Organizations.md", "\n".join(lines))

    def _gen_topics_index(self) -> None:
        """Generates Index - Topics.md using hierarchical hashtags and YAML descriptions."""
        if not self.topics_yaml or not self.topics_yaml.exists():
            return

        try:
            with open(self.topics_yaml, encoding="utf-8") as f:
                themes_data = yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to parse topics YAML: {e}")
            return

        # Get used topics
        used_topics = set()
        for entry in self.entries:
            for entity in entry.entities:
                if entity.prefix == "Category":
                    used_topics.add(entity.value)

        lines = ["# Index of Categories/Topics\n"]
        
        if not themes_data or not isinstance(themes_data, dict):
            return

        categories = themes_data.get("categories", [])
        for cat in categories:
            cat_name = cat.get("category")
            if not cat_name:
                continue
                
            cat_tag = f"#Category/{cat_name}"
            cat_desc = cat.get("description", "")
            
            topics = cat.get("topics", [])
            # Check if category or any of its subtopics are used
            has_used_st = any(
                f"#Category/{cat_name}/{t.get('topic')}" in used_topics for t in topics
            )
            
            if cat_tag in used_topics or has_used_st:
                lines.append(f"## {cat_tag}")
                if cat_desc:
                    lines.append(cat_desc)
                
                for topic in topics:
                    st_name = topic.get("topic")
                    st_desc = topic.get("description", "")
                    st_tag = f"#Category/{cat_name}/{st_name}"
                    if st_tag in used_topics:
                        lines.append(f"{st_tag} -- {st_desc}")

        self._write_index("Index - Topics.md", "\n".join(lines))
