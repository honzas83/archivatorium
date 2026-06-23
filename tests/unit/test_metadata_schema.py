import pytest
from pydantic import ValidationError

from archivatorium.models.metadata import MetadataSchema


def test_metadata_schema_defaults() -> None:
    # Test that all fields have reasonable defaults and are not None
    schema = MetadataSchema()
    assert schema.language == "English"
    assert schema.summary == ""
    assert schema.title == ""
    assert schema.sender == ""
    assert schema.item_type == "other"


def test_metadata_schema_valid_data() -> None:
    data = {
        "title": "Test Title",
        "language": "French",
        "archive_code": "NPG/D(77)12",
        "date": "1981-11-19",
        "summary": "First sentence. Second sentence.",
        "abstract": "First sentence. Second sentence. More detail.",
        "author_name": "D.A. NICHOLLS",
    }
    schema = MetadataSchema(**data)
    assert schema.title == "Test Title"
    assert schema.language == "French"
    assert schema.archive_code == "NPG/D(77)12"
    assert schema.summary == "First sentence. Second sentence."
    assert schema.abstract == "First sentence. Second sentence. More detail."


def test_metadata_schema_field_order_matches_generated_metadata_hierarchy() -> None:
    expected_prefix = [
        "item_type",
        "title",
        "summary",
        "abstract",
        "author_name",
        "author_institution",
        "date",
        "archive_code",
        "language",
        "location_city",
        "location_state",
        "sender",
        "recipient",
        "intent",
        "references",
    ]

    assert list(MetadataSchema.model_fields) == expected_prefix


@pytest.mark.parametrize(
    "item_type",
    [
        "correspondence",
        "report",
        "study",
        "meeting_minutes",
        "working_paper",
        "schedule",
        "corrigendum",
        "agenda",
        "press_release",
        "note",
        "directive",
        "other",
    ],
)
def test_metadata_schema_accepts_approved_item_types(item_type: str) -> None:
    schema = MetadataSchema(item_type=item_type)
    assert schema.item_type == item_type


@pytest.mark.parametrize("item_type", ["", None])
def test_metadata_schema_empty_item_type_defaults_to_other(item_type: str | None) -> None:
    schema = MetadataSchema(item_type=item_type)
    assert schema.item_type == "other"


@pytest.mark.parametrize(
    "item_type",
    [
        "minutes",
        "Meeting Minutes",
        "meeting minutes",
        "communique",
        "communiqué",
    ],
)
def test_metadata_schema_rejects_unapproved_item_types(item_type: str) -> None:
    with pytest.raises(ValidationError):
        MetadataSchema(item_type=item_type)


def test_metadata_schema_flattened_correspondence() -> None:
    data = {"sender": "Sender X", "recipient": "Recipient Y", "intent": "Action Z"}
    schema = MetadataSchema(**data)
    assert schema.sender == "Sender X"
    assert schema.recipient == "Recipient Y"
    assert schema.intent == "Action Z"
