from pathlib import Path

from archivatorium.models.metadata import CanonicalTags
from archivatorium.services.indexing_service import EntityReference, IndexEntry, IndexingService


def test_gen_topics_index(tmp_path: Path) -> None:
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()

    topics_yaml = tmp_path / "topics.yaml"
    topics_yaml.write_text(
        """
categories:
  - category: "Doctrine and Strategy"
    description: "Military doctrines."
    topics:
      - topic: "Nuclear Deterrence"
        description: "Nuclear strategy."
      - topic: "Conventional"
        description: "Conventional strategy."
""",
        encoding="utf-8",
    )

    indexer = IndexingService(vault_dir, topics_yaml=topics_yaml)

    tags = CanonicalTags(raw_paths={"Topics/Doctrine-and-Strategy/Nuclear-Deterrence"})
    indexer.entries = [
        IndexEntry(
            doc_path=Path("doc1.md"),
            canonical_tags=tags,
        )
    ]

    # Generate indices
    indexer.generate_markdown_indices()

    index_file = vault_dir / "Index - Topics.md"
    assert index_file.exists()

    content = index_file.read_text(encoding="utf-8")
    assert "# Index of Categories/Topics" in content
    # Header should be normalized
    assert "## #Category/Doctrine-and-Strategy" in content

    assert "Military doctrines." in content
    # Topic should be normalized and matched
    assert "#Category/Doctrine-and-Strategy/Nuclear-Deterrence -- Nuclear strategy." in content
    assert "#Category/Doctrine-and-Strategy/Conventional" not in content  # Not used


def test_gen_topics_index_ignores_legacy_topic_tags(tmp_path: Path) -> None:
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()
    topics_yaml = tmp_path / "topics.yaml"
    topics_yaml.write_text(
        """
categories:
  - category: "Doctrine and Strategy"
    topics:
      - topic: "Nuclear Deterrence"
        description: "Nuclear strategy."
""",
        encoding="utf-8",
    )
    indexer = IndexingService(vault_dir, topics_yaml=topics_yaml)
    indexer.entries = [
        IndexEntry(
            doc_path=Path("legacy.md"),
            entities=[
                EntityReference(
                    "Doctrine-and-Strategy",
                    "#Category/Doctrine-and-Strategy/Nuclear-Deterrence",
                    "Nuclear Deterrence",
                )
            ],
            canonical_tags=CanonicalTags(),
        )
    ]

    indexer.generate_markdown_indices()

    assert not (vault_dir / "Index - Topics.md").exists()
