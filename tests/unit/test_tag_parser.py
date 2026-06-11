from pathlib import Path
from typing import Any

from ocrpolish.utils.tag_parser import CanonicalTagParser


SLASH_ENTITY_TAG_TEXT = """
- #Entities/Org/OTAN/NATO
- #Entities/Org/NAC/DP
- #Entities/Org/Council/DPC
- #Entities/State/USA/California
"""


def test_parse_valid_tags() -> None:
    text = """
    This is some text containing:
    - #Entities/State/United-States
    - #Entities/Org/NATO
    - #Entities/Person/Joseph-Luns
    - #Entities/City/United-Kingdom/London
    - #Topics/Force-Planning/Command-Structure
    - #Tags/Strategic-Concept
    """
    parser = CanonicalTagParser()
    tags = parser.parse_text(text, file_path=Path("test.md"))

    # Test raw paths (without #)
    assert tags.raw_paths == {
        "Entities/State/United-States",
        "Entities/Org/NATO",
        "Entities/Person/Joseph-Luns",
        "Entities/City/United-Kingdom/London",
        "Topics/Force-Planning/Command-Structure",
        "Tags/Strategic-Concept",
    }

    # Test conceptual tags
    assert tags.conceptual_tags == {"strategic-concept"}

    # Test topics
    assert tags.topics == {"force-planning/command-structure"}

    # Test entities
    assert tags.entities["State"] == {"united-states"}
    assert tags.entities["Org"] == {"nato"}
    assert tags.entities["Person"] == {"joseph-luns"}
    assert tags.entities["City"] == {"united-kingdom/london"}


def test_ignore_legacy_and_unprefixed_tags() -> None:
    text = """
    #Nuclear-Deterrence
    #Category/Military-Strategy
    #Cat/Topic
    #Entities/State/France
    """
    parser = CanonicalTagParser()
    tags = parser.parse_text(text)

    # Only Entities/State/France should be parsed
    assert tags.raw_paths == {"Entities/State/France"}
    assert tags.entities["State"] == {"france"}


def test_normalize_components() -> None:
    text = """
    #Entities/State/United States
    #Entities/Org/NATO_Allies
    #Tags/Strategic Concept
    #Topics/Force Planning/Command Structure
    """
    parser = CanonicalTagParser()
    tags = parser.parse_text(text)

    # Note: Obsidian tags do not allow spaces, but our parser handles them
    # if matched, or normalizes parts with normalize_tag_component.
    # Let's test that normalization rules (like camelCase preservation, replacing spaces/special characters with hyphens) apply.
    assert "Entities/State/United-States" in tags.raw_paths
    assert "Entities/Org/NATO-Allies" in tags.raw_paths
    assert "Tags/Strategic-Concept" in tags.raw_paths
    assert "Topics/Force-Planning/Command-Structure" in tags.raw_paths


def test_deduplicate_values() -> None:
    text = """
    #Entities/State/France
    #Entities/State/France
    #Tags/Deterrence
    #Tags/Deterrence
    """
    parser = CanonicalTagParser()
    tags = parser.parse_text(text)

    assert len(tags.entities["State"]) == 1
    assert tags.entities["State"] == {"france"}
    assert tags.conceptual_tags == {"deterrence"}


def test_parse_hierarchical_conceptual_tags() -> None:
    text = "#Tags/WINTEX/73 #Tags/Exercise/Series/1973"
    parser = CanonicalTagParser()
    tags = parser.parse_text(text)

    assert tags.conceptual_tags == {"wintex/73", "exercise/series/1973"}
    assert "Tags/WINTEX/73" in tags.raw_paths
    assert "Tags/Exercise/Series/1973" in tags.raw_paths


def test_parse_slash_containing_org_and_state_names() -> None:
    parser = CanonicalTagParser()
    tags = parser.parse_text(SLASH_ENTITY_TAG_TEXT)

    assert "Entities/Org/OTAN-NATO" in tags.raw_paths
    assert "Entities/Org/NAC-DP" in tags.raw_paths
    assert "Entities/Org/Council-DPC" in tags.raw_paths
    assert "Entities/State/USA-California" in tags.raw_paths
    assert tags.entities["Org"] >= {"otan-nato", "nac-dp", "council-dpc"}
    assert "usa-california" in tags.entities["State"]


def test_slash_containing_org_and_state_names_do_not_warn(caplog: Any) -> None:
    parser = CanonicalTagParser()

    tags = parser.parse_text(SLASH_ENTITY_TAG_TEXT)

    assert "Entities/Org/OTAN-NATO" in tags.raw_paths
    assert not [
        record
        for record in caplog.records
        if "Malformed generated tag ignored" in record.getMessage()
    ]
