from ocrpolish.models.metadata import MetadataSchema


def test_metadata_schema_defaults():
    # Test that all fields have reasonable defaults and are not None
    schema = MetadataSchema()
    assert schema.language == "English"
    assert schema.summary == ""
    assert schema.title == ""
    assert schema.mentioned_states == []
    assert schema.correspondence_sender == ""

def test_metadata_schema_valid_data():
    data = {
        "title": "Test Title",
        "language": "French",
        "archive_code": "NPG/D(77)12",
        "date": "1981-11-19",
        "summary": "First sentence. Second sentence.",
        "abstract": "First sentence. Second sentence. More detail.",
        "author_name": "D.A. NICHOLLS",
        "mentioned_states": ["Greece"]
    }
    schema = MetadataSchema(**data)
    assert schema.title == "Test Title"
    assert schema.language == "French"
    assert schema.archive_code == "NPG/D(77)12"
    assert schema.summary == "First sentence. Second sentence."
    assert schema.abstract == "First sentence. Second sentence. More detail."
    assert "Greece" in schema.mentioned_states

def test_metadata_schema_flattened_correspondence():
    data = {
        "correspondence_sender": "Sender X",
        "correspondence_recipient": "Recipient Y",
        "correspondence_transaction": "Action Z"
    }
    schema = MetadataSchema(**data)
    assert schema.correspondence_sender == "Sender X"
    assert schema.correspondence_recipient == "Recipient Y"
    assert schema.correspondence_transaction == "Action Z"
