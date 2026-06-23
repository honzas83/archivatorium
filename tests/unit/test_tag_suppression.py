from archivatorium.utils.nlp import suppress_duplicates


def test_suppress_duplicates_basic():
    conceptual = ["#NATO", "#Exercise", "#Logistics"]
    entities = ["Org/NATO"]
    topics = ["Category/Military/Logistics"]

    # NATO and Logistics should be suppressed because they appear in entities/topics
    result = suppress_duplicates(conceptual, entities, topics)
    assert "#Exercise" in result
    assert "#NATO" not in result
    assert "#Logistics" not in result


def test_suppress_duplicates_hierarchical():
    conceptual = ["#Germany", "#Berlin", "#Strategy"]
    entities = ["State/Germany", "City/Germany/Berlin"]
    topics = ["Category/Defense/Strategy"]

    result = suppress_duplicates(conceptual, entities, topics)
    assert result == []


def test_suppress_duplicates_case_insensitivity():
    conceptual = ["#nato"]
    entities = ["Org/NATO"]
    topics: list[str] = []

    result = suppress_duplicates(conceptual, entities, topics)
    assert result == []


def test_suppress_duplicates_no_duplicates():
    conceptual = ["#NewTag"]
    entities = ["Org/NATO"]
    topics = ["Category/Defense"]

    result = suppress_duplicates(conceptual, entities, topics)
    assert result == ["#NewTag"]
