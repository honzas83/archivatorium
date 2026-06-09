from pathlib import Path

from ocrpolish.models.metadata import CanonicalTags
from ocrpolish.services.indexing_service import IndexEntry, IndexingService


def test_markdown_indices_generation(tmp_path: Path) -> None:
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()

    service = IndexingService(vault_dir)

    # Mock index entry 1
    tags1 = CanonicalTags()
    tags1.raw_paths = {
        "Entities/State/US",
        "Entities/Org/NATO",
        "Entities/City/US/Washington",
        "Entities/Person/Luns",
        "Topics/Defense",
        "Tags/Strategy",
    }
    entry1 = IndexEntry(
        doc_path=Path("doc1.md"),
        title="Document One",
        canonical_tags=tags1,
    )

    # Mock index entry 2
    tags2 = CanonicalTags()
    tags2.raw_paths = {
        "Entities/State/Belgium",
        "Entities/City/Belgium/Brussels",
        "Entities/Org/NATO",
        "Tags/Tactics",
    }
    entry2 = IndexEntry(
        doc_path=Path("doc2.md"),
        title="Document Two",
        canonical_tags=tags2,
    )

    service.entries = [entry1, entry2]
    service.generate_markdown_indices()

    # Check States index
    states_content = (vault_dir / "Index - States.md").read_text(encoding="utf-8")
    assert "## B" in states_content
    assert "### #Entities/State/Belgium" in states_content
    assert "- [[doc2.md|Document Two]]" in states_content
    assert "## U" in states_content
    assert "### #Entities/State/US" in states_content
    assert "- [[doc1.md|Document One]]" in states_content

    # Check Cities index
    cities_content = (vault_dir / "Index - Cities.md").read_text(encoding="utf-8")
    assert "## Belgium" in cities_content
    assert "### #Entities/City/Belgium/Brussels" in cities_content
    assert "- [[doc2.md|Document Two]]" in cities_content
    assert "## US" in cities_content
    assert "### #Entities/City/US/Washington" in cities_content

    # Check Orgs index
    orgs_content = (vault_dir / "Index - Organizations.md").read_text(encoding="utf-8")
    assert "### #Entities/Org/NATO" in orgs_content
    assert "- [[doc1.md|Document One]]" in orgs_content
    assert "- [[doc2.md|Document Two]]" in orgs_content

    # Check People index
    people_content = (vault_dir / "Index - People.md").read_text(encoding="utf-8")
    assert "### #Entities/Person/Luns" in people_content

    # Check Topics index
    topics_content = (vault_dir / "Index - Topics.md").read_text(encoding="utf-8")
    assert "### #Topics/Defense" in topics_content

    # Check Tags index
    tags_content = (vault_dir / "Index - Tags.md").read_text(encoding="utf-8")
    assert "### #Tags/Strategy" in tags_content
    assert "### #Tags/Tactics" in tags_content
