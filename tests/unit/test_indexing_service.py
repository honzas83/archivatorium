from pathlib import Path

from ocrpolish.services.indexing_service import EntityReference, IndexingService


def test_parse_entity() -> None:
    indexer = IndexingService(Path("."))

    # Valid entities
    assert indexer._parse_entity("#State/Belgium") == EntityReference(
        "State", "#State/Belgium", "Belgium"
    )
    assert indexer._parse_entity("#City/Belgium/Brussels") == EntityReference(
        "City", "#City/Belgium/Brussels", "Brussels"
    )
    assert indexer._parse_entity("#Org/NATO") == EntityReference("Org", "#Org/NATO", "NATO")

    # Invalid entities
    assert indexer._parse_entity("#Unknown/Something") is None
    assert indexer._parse_entity("NoHash/State/Belgium") is None
    assert indexer._parse_entity("#State") is None  # No sub-parts


def test_process_file_with_abstract(tmp_path: Path) -> None:
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()

    doc_path = vault_dir / "test.md"
    doc_path.write_text(
        """---
title: Test Doc
summary: This is a test.
tags: ["#State/Belgium", "TagWithoutHash"]
---
> [!abstract]
> This document mentions #Org/NATO and #City/Belgium/Brussels.
> It also repeats #State/Belgium.
""",
        encoding="utf-8",
    )

    indexer = IndexingService(vault_dir)
    indexer.process_file(doc_path)

    assert len(indexer.entries) == 1
    entry = indexer.entries[0]
    assert entry.title == "Test Doc"

    # Check entities: Belgium (FM), NATO (Abstract), Brussels (Abstract)
    # TagWithoutHash should be ignored unless it has an indexing prefix
    entity_values = [e.value for e in entry.entities]
    assert "#State/Belgium" in entity_values
    assert "#Org/NATO" in entity_values
    assert "#City/Belgium/Brussels" in entity_values
    assert len(entity_values) == 3


def test_utf8_error_handling(tmp_path: Path) -> None:
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()

    doc_path = vault_dir / "bad_utf8.md"
    # Write some invalid UTF-8 bytes
    with open(doc_path, "wb") as f:
        f.write(b"--- \ntitle: Bad UTF8\n---\n \xfe\xff")

    indexer = IndexingService(vault_dir)
    # Should not raise exception
    indexer.process_file(doc_path)
    assert len(indexer.entries) == 1
    assert indexer.entries[0].title == "Bad UTF8"
