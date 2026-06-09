from ocrpolish.models.metadata import MetadataSchema


def test_metadata_schema_defaults() -> None:
    # Test that all fields have reasonable defaults and are not None
    schema = MetadataSchema()
    assert schema.language == "English"
    assert schema.summary == ""
    assert schema.title == ""
    assert schema.sender == ""


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


def test_metadata_schema_flattened_correspondence() -> None:
    data = {"sender": "Sender X", "recipient": "Recipient Y", "intent": "Action Z"}
    schema = MetadataSchema(**data)
    assert schema.sender == "Sender X"
    assert schema.recipient == "Recipient Y"
    assert schema.intent == "Action Z"
