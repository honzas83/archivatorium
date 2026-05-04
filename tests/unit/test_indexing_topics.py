from pathlib import Path

from ocrpolish.services.indexing_service import EntityReference, IndexEntry, IndexingService


def test_gen_topics_index(tmp_path: Path) -> None:
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()

    topics_yaml = tmp_path / "topics.yaml"
    topics_yaml.write_text(
        """
categories:
  - category: "Doctrine"
    description: "Military doctrines."
    topics:
      - topic: "Nuclear"
        description: "Nuclear strategy."
      - topic: "Conventional"
        description: "Conventional strategy."
""",
        encoding="utf-8",
    )

    indexer = IndexingService(vault_dir, topics_yaml=topics_yaml)

    # Mock entries
    indexer.entries = [
        IndexEntry(
            doc_path=Path("doc1.md"),
            entities=[EntityReference("Category", "#Category/Doctrine/Nuclear", "Nuclear")],
        )
    ]

    # We need to mock _write_index or just let it write to tmp_path
    # IndexingService._write_index writes to self.input_dir
    indexer.generate_markdown_indices()

    index_file = vault_dir / "Index - Topics.md"
    assert index_file.exists()

    content = index_file.read_text(encoding="utf-8")
    assert "# Index of Categories/Topics" in content
    assert "## #Category/Doctrine" in content
    assert "Military doctrines." in content
    assert "#Category/Doctrine/Nuclear -- Nuclear strategy." in content
    assert "#Category/Doctrine/Conventional" not in content  # Not used
