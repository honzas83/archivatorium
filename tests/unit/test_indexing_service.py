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


def test_index_page_capping(tmp_path: Path) -> None:
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()

    tags = CanonicalTags()
    tags.raw_paths.add("Tags/DefencePlanning")
    tags.raw_paths.add("Entities/City/Belgium/Brussels")

    entries = []
    # Create 55 entries linking to the same tag/city
    for idx in range(55):
        entries.append(
            IndexEntry(
                doc_path=Path(f"doc_{idx}.md"),
                title=f"Doc {idx}",
                canonical_tags=tags,
            )
        )

    indexer = IndexingService(vault_dir)
    indexer.entries = entries
    indexer.generate_markdown_indices()

    # 1. Verify Index - Tags.md
    tags_index_file = vault_dir / "Index - Tags.md"
    assert tags_index_file.exists()
    tags_content = tags_index_file.read_text(encoding="utf-8")

    # Should list exactly 50 doc links
    link_count = tags_content.count("[[doc_")
    assert link_count == 50
    # Should contain the suffix search query
    assert (
        "and 5 more. [Search in Vault](obsidian://search?vault=vault&query=tag%3A%23Tags/DefencePlanning)"
        in tags_content
    )

    # 2. Verify Index - Cities.md
    cities_index_file = vault_dir / "Index - Cities.md"
    assert cities_index_file.exists()
    cities_content = cities_index_file.read_text(encoding="utf-8")

    city_link_count = cities_content.count("[[doc_")
    assert city_link_count == 50
    assert (
        "and 5 more. [Search in Vault](obsidian://search?vault=vault&query=tag%3A%23Entities/City/Belgium/Brussels)"
        in cities_content
    )


def test_people_index_groups_full_paths_by_surname(tmp_path: Path) -> None:
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()
    tags = CanonicalTags(
        raw_paths={
            "Entities/Person/Andrae",
            "Entities/Person/Andrae/K-W",
            "Entities/Person/Andrae/Joseph",
            "Entities/Person/Luns/Joseph-M-A-H",
        }
    )
    indexer = IndexingService(vault_dir)
    indexer.entries = [
        IndexEntry(doc_path=Path("people.md"), title="People", canonical_tags=tags)
    ]

    indexer.generate_markdown_indices()

    content = (vault_dir / "Index - People.md").read_text(encoding="utf-8")
    assert content.count("## A") == 1
    assert content.count("## L") == 1
    assert content.index("## A") < content.index("## L")
    assert content.count("### #Entities/Person/Andrae") == 3
    assert "### #Entities/Person/Luns/Joseph-M-A-H" in content
