from pathlib import Path

import openpyxl  # type: ignore

from ocrpolish.models.metadata import CanonicalTags
from ocrpolish.services.indexing_service import EntityReference, IndexEntry, IndexingService


def test_xlsx_generation(tmp_path: Path) -> None:
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()

    service = IndexingService(vault_dir)

    tags = CanonicalTags()
    tags.raw_paths = {
        "Entities/State/US",
        "Entities/Org/NATO",
        "Entities/City/US/Washington",
        "Topics/Defense",
        "Tags/Strategy",
    }
    entry = IndexEntry(
        doc_path=Path("doc1.md"),
        title="Document One",
        summary="A test document summary.",
        date="1974-05-15",
        raw_metadata={
            "archive_code": "NPG/D(74)2",
            "citekey": "NPG-D-74-2",
            "language": "English",
            "location_city": "Washington",
            "location_state": "US",
            "sender": "NATO Secretary General",
            "recipient": "Planning Group",
            "intent": "Discuss defense strategy.",
            "references": ["NPG/D(73)1"],
        },
        canonical_tags=tags,
    )

    service.entries = [entry]
    xlsx_path = vault_dir / "metadata_index.xlsx"
    service.generate_xlsx(xlsx_path)

    assert xlsx_path.exists()

    # Load with openpyxl to verify cell content
    wb = openpyxl.load_workbook(xlsx_path)
    sheet = wb["Metadata Index"]

    # Verify headers
    headers = [cell.value for cell in sheet[1]]
    assert "File Path" in headers
    assert "Citekey" in headers
    assert "state_entities" in headers
    assert "org_entities" in headers
    assert "city_entities" in headers

    # Verify values
    row_values = [cell.value for cell in sheet[2]]
    # Mapping fields: doc_path is at col 0, Citekey is at col 1, Title at col 2
    assert row_values[0] == "doc1.md"
    assert row_values[1] == "NPG-D-74-2"
    assert row_values[2] == "Document One"
    assert row_values[3] == "A test document summary."
    assert row_values[4] == "1974-05-15"

    # Verify pivoted tag values are formatted correctly with #
    # state_entities is in tag_fields, let's find it by header index
    state_col = headers.index("state_entities")
    assert row_values[state_col] == "#Entities/State/US"

    org_col = headers.index("org_entities")
    assert row_values[org_col] == "#Entities/Org/NATO"


def test_xlsx_export_does_not_migrate_legacy_tags(tmp_path: Path) -> None:
    vault_dir = tmp_path / "vault"
    vault_dir.mkdir()
    service = IndexingService(vault_dir)
    entry = IndexEntry(
        doc_path=Path("legacy.md"),
        title="Legacy",
        canonical_tags=CanonicalTags(),
    )
    entry.entities = [
        EntityReference("State", "#State/Belgium", "Belgium"),
        EntityReference("Org", "#Org/NATO", "NATO"),
        EntityReference("City", "#City/Belgium/Brussels", "Brussels"),
        EntityReference("Person", "#Person/Smith", "Smith"),
        EntityReference("Category", "#Category/Nuclear", "Nuclear"),
    ]
    service.entries = [entry]
    xlsx_path = vault_dir / "metadata_index.xlsx"

    service.generate_xlsx(xlsx_path)

    wb = openpyxl.load_workbook(xlsx_path)
    sheet = wb["Metadata Index"]
    headers = [cell.value for cell in sheet[1]]
    row_values = [cell.value for cell in sheet[2]]

    for column in [
        "conceptual_tags",
        "topic_tags",
        "state_entities",
        "org_entities",
        "city_entities",
        "person_entities",
    ]:
        assert row_values[headers.index(column)] in (None, "")
