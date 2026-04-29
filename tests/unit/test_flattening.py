import pytest
from ocrpolish.services.flattening_service import FlatteningService

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
                        "negative_samples": "Neg 1.1"
                    },
                    {
                        "topic": "Topic 2",
                        "description": "Desc 2",
                        "positive_samples": "Pos 2.1"
                    }
                ]
            },
            {
                "category": "Category B",
                "topics": [
                    {
                        "topic": "Topic 3",
                        "description": "Desc 3"
                    }
                ]
            }
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

def test_flatten_no_samples(sample_hierarchy):
    service = FlatteningService()
    flat = service.flatten(sample_hierarchy)
    
    # Topic 3 has no samples
    assert "positive_samples" not in flat[2]
    assert "negative_samples" not in flat[2]
