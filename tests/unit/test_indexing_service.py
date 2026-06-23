from pathlib import Path

from archivatorium.models.metadata import CanonicalTags
from archivatorium.services.indexing_service import EntityReference, IndexEntry, IndexingService


def test_process_file_with_abstract(tmp_path: Path) -> None:
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()

    doc_path = vault_dir / "test.md"
    doc_path.write_text(
        """---
title: Test Doc
summary: This is a test.
tags: ["#Entities/State/Belgium", "TagWithoutHash"]
---
> [!abstract]
> This document mentions #Entities/Org/NATO and #Entities/City/Belgium/Brussels.
> It also repeats #Entities/State/Belgium.
""",
        encoding="utf-8",
    )

    indexer = IndexingService(vault_dir)
    indexer.process_file(doc_path)

    assert len(indexer.entries) == 1
    entry = indexer.entries[0]
    assert entry.title == "Test Doc"

    # Check entities: Belgium, NATO, Brussels
    entity_values = [e.value for e in entry.entities]
    assert "#Entities/State/Belgium" in entity_values
    assert "#Entities/Org/NATO" in entity_values
    assert "#Entities/City/Belgium/Brussels" in entity_values
    assert len(entity_values) == 3


def test_utf8_error_handling(tmp_path: Path) -> None:
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()

    doc_path = vault_dir / "bad_utf8.md"
    with open(doc_path, "wb") as f:
        f.write(b"--- \ntitle: Bad UTF8\n---\n \xfe\xff")

    indexer = IndexingService(vault_dir)
    indexer.process_file(doc_path)
    assert len(indexer.entries) == 1
    assert indexer.entries[0].title == "Bad UTF8"


def test_process_file_ignores_obsolete_unprefixed_tags(tmp_path: Path) -> None:
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()
    doc_path = vault_dir / "legacy.md"
    doc_path.write_text(
        """---
title: Legacy
---
#State/Belgium #Org/NATO #City/Belgium/Brussels #Person/Smith #Category/Nuclear #Topic/Legacy
#Entities/Org/SHAPE #Tags/Canonical
""",
        encoding="utf-8",
    )

    indexer = IndexingService(vault_dir)
    indexer.process_file(doc_path)

    entry = indexer.entries[0]
    assert entry.canonical_tags.raw_paths == {"Entities/Org/SHAPE", "Tags/Canonical"}


def test_markdown_index_ignores_legacy_entity_reference_fallback(tmp_path: Path) -> None:
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()
    indexer = IndexingService(vault_dir)
    indexer.entries = [
        IndexEntry(
            doc_path=Path("legacy.md"),
            entities=[EntityReference("State", "#Belgium", "Belgium")],
            canonical_tags=CanonicalTags(),
        )
    ]

    indexer.generate_markdown_indices()

    assert not (vault_dir / "Index - States.md").exists()
