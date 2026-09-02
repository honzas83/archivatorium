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


def test_suppress_duplicates_uses_every_meaningful_entity_path_component():
    conceptual = ["#Luns", "#Joseph-M-A-H", "#Belgium", "#Brussels", "#Consultation"]
    entities = ["Person/Luns/Joseph-M-A-H", "City/Belgium/Brussels"]

    result = suppress_duplicates(conceptual, entities, [])

    assert result == ["#Consultation"]


def test_protected_vocabulary_cannot_bypass_entity_collision():
    result = suppress_duplicates(
        ["#NATO", "#Nuclear-Planning"],
        ["Org/N.A.T.O."],
        [],
        protected_terms={"nato", "nuclear-planning"},
    )

    assert result == ["#Nuclear-Planning"]
