from copy import deepcopy

import pytest

from archivatorium.services.flattening_service import FlatteningService, TaxonomyValidationError


@pytest.fixture
def sample_hierarchy():
    return {
        "categories": [
            {
                "category": "Category A",
                "description": "Desc A",
                "topics": [
                    {
                        "topic": "Topic 1",
                        "description": "Desc 1",
                        "positive_samples": "Pos 1.1\nPos 1.2\nPos 1.3",
                        "negative_samples": "Neg 1.1",
                    },
                    {
                        "topic": "Topic 2",
                        "description": "Desc 2",
                        "positive_samples": "Pos 2.1",
                        "negative_samples": "Neg 2.1",
                    },
                ],
            },
            {
                "category": "Category B",
                "description": "Desc B",
                "topics": [
                    {
                        "topic": "Topic 3",
                        "description": "Desc 3",
                        "positive_samples": "Pos 3.1",
                        "negative_samples": "Neg 3.1",
                    }
                ],
            },
        ]
    }


def test_flatten_basic(sample_hierarchy):
    service = FlatteningService()
    flat = service.flatten(sample_hierarchy)

    assert len(flat) == 3
    assert flat[0]["id"] == "Category A/Topic 1"
    assert flat[0]["description"] == "Desc 1"
    assert flat[1]["id"] == "Category A/Topic 2"
    assert flat[2]["id"] == "Category B/Topic 3"


def test_flatten_all_samples(sample_hierarchy):
    service = FlatteningService()
    flat = service.flatten(sample_hierarchy)

    # Check Topic 1 positive samples - all should be included
    pos_samples = flat[0]["positive_samples"]
    assert len(pos_samples) == 3
    assert pos_samples == ["Pos 1.1", "Pos 1.2", "Pos 1.3"]

    # Check Topic 1 negative samples
    neg_samples = flat[0]["negative_samples"]
    assert len(neg_samples) == 1
    assert neg_samples == ["Neg 1.1"]


def test_flatten_preserves_complete_category_and_topic_context(sample_hierarchy):
    flat = FlatteningService().flatten(sample_hierarchy)

    assert flat[0] == {
        "id": "Category A/Topic 1",
        "category": "Category A",
        "category_description": "Desc A",
        "description": "Desc 1",
        "positive_samples": ["Pos 1.1", "Pos 1.2", "Pos 1.3"],
        "negative_samples": ["Neg 1.1"],
    }
    assert flat[2]["category"] == "Category B"
    assert flat[2]["category_description"] == "Desc B"
    assert flat[2]["description"] == "Desc 3"


@pytest.mark.parametrize(
    ("mutator", "message"),
    [
        (lambda data: data.update(categories="wrong"), "categories"),
        (lambda data: data["categories"][0].update(description=" "), "description"),
        (
            lambda data: data["categories"][0]["topics"][0].update(description=""),
            "description",
        ),
        (
            lambda data: data["categories"][0]["topics"][0].update(positive_samples=["bad"]),
            "positive_samples",
        ),
        (lambda data: data["categories"][0].update(category="Bad/Category"), "/"),
        (lambda data: data["categories"][0]["topics"][0].update(topic="Bad/Topic"), "/"),
    ],
)
def test_flatten_rejects_invalid_structure(sample_hierarchy, mutator, message):
    hierarchy = deepcopy(sample_hierarchy)
    mutator(hierarchy)

    with pytest.raises(TaxonomyValidationError, match=message):
        FlatteningService().flatten(hierarchy)


def test_flatten_rejects_non_mapping_root():
    with pytest.raises(TaxonomyValidationError, match="root"):
        FlatteningService().flatten([])  # type: ignore[arg-type]


def test_flatten_rejects_normalized_path_collision(sample_hierarchy):
    hierarchy = deepcopy(sample_hierarchy)
    hierarchy["categories"][0]["topics"].append(
        {
            "topic": "Topic-1",
            "description": "Colliding topic",
            "positive_samples": "Positive",
            "negative_samples": "Negative",
        }
    )

    with pytest.raises(TaxonomyValidationError, match="duplicate"):
        FlatteningService().flatten(hierarchy)


def test_flatten_rejects_schema_v2_without_policy(sample_hierarchy):
    hierarchy = deepcopy(sample_hierarchy)
    hierarchy["schema_version"] = 2

    with pytest.raises(TaxonomyValidationError, match="classification_policy"):
        FlatteningService().flatten(hierarchy)
