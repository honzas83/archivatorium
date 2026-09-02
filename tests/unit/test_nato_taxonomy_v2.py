import hashlib
from pathlib import Path
from typing import Any, cast

import yaml

from archivatorium.services.flattening_service import FlatteningService

ROOT = Path(__file__).parents[2]
V1_PATH = ROOT / "topics" / "NATO_themes.yaml"
V2_PATH = ROOT / "topics" / "NATO_themes_v2.yaml"
V1_SHA256 = "90daa6f599decda1c6fed633a83b99d95362a59abb2eac4e9c1d61a6f4bf515a"

EXPECTED_COUNTS = {
    "Nuclear Doctrine and Deterrence": 6,
    "Nuclear Planning, Deployment, and Control": 7,
    "Alliance Governance and Institutions": 9,
    "Treaties and Arms Control": 7,
    "Military Operations and Capabilities": 13,
    "Geopolitics and Crises": 13,
}


def _load_v2() -> dict[str, Any]:
    with V2_PATH.open(encoding="utf-8") as stream:
        return cast(dict[str, Any], yaml.safe_load(stream))


def _topic(data: dict[str, Any], category_name: str, topic_name: str) -> dict[str, Any]:
    category = next(item for item in data["categories"] if item["category"] == category_name)
    return next(item for item in category["topics"] if item["topic"] == topic_name)


def test_v1_taxonomy_is_byte_for_byte_unchanged() -> None:
    assert hashlib.sha256(V1_PATH.read_bytes()).hexdigest() == V1_SHA256


def test_v2_has_exact_categories_counts_and_unique_paths() -> None:
    data = _load_v2()
    counts = {category["category"]: len(category["topics"]) for category in data["categories"]}

    assert data["schema_version"] == 2
    assert counts == EXPECTED_COUNTS
    flattened = FlatteningService().flatten(data)
    assert len(flattened) == 55
    assert len({topic["id"] for topic in flattened}) == 55


def test_v2_places_split_renamed_and_moved_topics() -> None:
    data = _load_v2()
    expected_paths = {
        "Nuclear Doctrine and Deterrence/Extended Nuclear Deterrence",
        "Nuclear Planning, Deployment, and Control/Nuclear Sharing and Forward Deployment",
        "Nuclear Planning, Deployment, and Control/Nuclear Release Authority",
        "Alliance Governance and Institutions/Command Structure and Appointments",
        "Alliance Governance and Institutions/NATO Infrastructure and Common Funding",
        "Alliance Governance and Institutions/Article 5 Collective Defense",
        "Military Operations and Capabilities/Civil Emergency Planning",
    }
    paths = {topic["id"] for topic in FlatteningService().flatten(data)}

    assert expected_paths <= paths
    assert not any("Extended Deterrence and Tactical Nuclear Sharing" in path for path in paths)
    assert not any("Command and Control Authority" in path for path in paths)
    assert not any("Specific Commands and Infrastructure" in path for path in paths)


def test_v2_encodes_reviewed_inclusion_and_exclusion_boundaries() -> None:
    data = _load_v2()

    extended = _topic(data, "Nuclear Doctrine and Deterrence", "Extended Nuclear Deterrence")
    assert "protective guarantee" in extended["description"].lower()
    assert "stationed" in extended["negative_samples"].lower()

    sharing = _topic(
        data,
        "Nuclear Planning, Deployment, and Control",
        "Nuclear Sharing and Forward Deployment",
    )
    assert "custody" in sharing["description"].lower()
    assert "security" in sharing["negative_samples"].lower()

    release = _topic(data, "Nuclear Planning, Deployment, and Control", "Nuclear Release Authority")
    assert "dual-key" in release["positive_samples"].lower()

    strike = _topic(
        data,
        "Nuclear Planning, Deployment, and Control",
        "Nuclear Strategy and Strike Planning",
    )
    assert "target selection" in strike["description"].lower()
    assert "meeting" in strike["negative_samples"].lower()

    consultation = _topic(
        data, "Alliance Governance and Institutions", "Political Consultation Mechanisms"
    )
    assert "align policy" in consultation["description"].lower()
    assert "attendance" in consultation["negative_samples"].lower()

    neutral = _topic(data, "Geopolitics and Crises", "Neutral and Non-Aligned Nations")
    assert "Norway" not in neutral["positive_samples"]
    assert "mere mention" in neutral["negative_samples"].lower()

    intelligence = _topic(data, "Military Operations and Capabilities", "Intelligence Sharing")
    assert "exchange" in intelligence["description"].lower()
    assert "leak" in intelligence["negative_samples"].lower()

    spending = _topic(data, "Alliance Governance and Institutions", "Defense Spending")
    assert "budget" in spending["description"].lower()
    assert "restructuring" in spending["negative_samples"].lower()

    warsaw = _topic(data, "Geopolitics and Crises", "Warsaw Pact")
    assert "passing" in warsaw["negative_samples"].lower()
