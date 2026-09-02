from pathlib import Path
from unittest.mock import MagicMock
from zipfile import ZipFile

from archivatorium.models.metadata import WindowTaggingResult
from archivatorium.processor_metadata import MetadataProcessor
from archivatorium.services.indexing_service import IndexingService
from archivatorium.services.tagging_service import TaggingService


def test_person_hierarchy_survives_archive_consumers(tmp_path: Path) -> None:
    hierarchy = tmp_path / "hierarchy.yaml"
    hierarchy.write_text(
        """
classification_policy:
  substantive_subject_rule: Important subject only.
  omission_rule: Omit weak matches.
  insufficient_evidence_rule: Passing mentions are insufficient.
categories:
  - category: Diplomacy
    description: Diplomatic subjects
    topics:
      - topic: Negotiation
        description: Substantive negotiations
        positive_samples: A negotiated agreement
        negative_samples: A passing mention
""",
        encoding="utf-8",
    )
    client = MagicMock()
    client.extract_structured.return_value = WindowTaggingResult(
        conceptual_tags=["Diplomacy"],
        entity_tags=["Person/Andrae/K. W.", "Person/Luns"],
    )
    tagging = TaggingService(client, MagicMock(), hierarchy)
    tagged = tagging.extract_tags("K. W. Andrae and Luns negotiated the agreement.")
    assert tagged.entity_tags == ["Person/Andrae/K-W", "Person/Luns"]

    vault = tmp_path / "vault"
    vault.mkdir()
    processor = MetadataProcessor(MagicMock(), vault, tagging_service=tagging)
    sections = processor._format_generated_tags(tagged)
    assert "#Entities/Person/Andrae/K-W" in sections.entity_section_body
    assert "#Entities/Person/Luns" in sections.entity_section_body

    document = vault / "document.md"
    document.write_text(
        "---\ntitle: People\nsummary: Synthetic document.\n---\n\n"
        f"## Entities\n\n{sections.entity_section_body}\n",
        encoding="utf-8",
    )
    processor.preflight_scan()
    assert processor.entity_counts["Person"] == {
        "andrae/k-w": 1,
        "luns": 1,
    }
    assert processor._build_tagging_reuse_hints().preferred_entities["Person"] == [
        "andrae/k-w",
        "luns",
    ]

    indexer = IndexingService(vault)
    indexer.process_file(document)
    xlsx = vault / "metadata.xlsx"
    indexer.generate_xlsx(xlsx)
    with ZipFile(xlsx) as archive:
        workbook_text = "\n".join(
            archive.read(name).decode("utf-8")
            for name in archive.namelist()
            if name.endswith(".xml")
        )
    assert "#Entities/Person/Andrae/K-W" in workbook_text
    assert "#Entities/Person/Luns" in workbook_text
