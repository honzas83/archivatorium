from pathlib import Path

from ocrpolish.services.indexing_service import EntityReference, IndexEntry, IndexingService


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

    # Mock entries with legacy style tags
    indexer.entries = [
        IndexEntry(
            doc_path=Path("doc1.md"),
            entities=[
                EntityReference(
                    "Doctrine-and-Strategy",
                    "#Doctrine-and-Strategy/Nuclear-Deterrence",
                    "Nuclear Deterrence",
                )
            ],
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
    assert (
        "#Category/Doctrine-and-Strategy/Nuclear-Deterrence -- Nuclear strategy."
        in content
    )
    assert "#Category/Doctrine-and-Strategy/Conventional" not in content  # Not used
