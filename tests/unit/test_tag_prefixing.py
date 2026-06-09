from ocrpolish.data_model import TAG_PREFIX_ENTITY, TAG_PREFIX_TAG, TAG_PREFIX_TOPIC
from ocrpolish.utils.metadata import prefix_tag


def test_prefix_tag_with_constants():
    # Use global defaults from data_model
    assert prefix_tag("Strategy", TAG_PREFIX_TOPIC) == f"#{TAG_PREFIX_TOPIC}/Strategy"
    assert (
        prefix_tag("State/United-Kingdom", TAG_PREFIX_ENTITY)
        == f"#{TAG_PREFIX_ENTITY}/State/United-Kingdom"
    )
    assert prefix_tag("Reforger", TAG_PREFIX_TAG) == f"#{TAG_PREFIX_TAG}/Reforger"


def test_prefix_tag_none_opt_out():
    # If prefix is None, only normalization and hash should be applied
    assert prefix_tag("Strategy", None) == "#Strategy"
    assert prefix_tag("Nuclear Deterrence", None) == "#Nuclear-Deterrence"
    assert prefix_tag("State/United Kingdom", None) == "#State/United-Kingdom"


def test_prefix_tag_idempotency():
    # Should not double-prefix if already present
    prefix = "Topics"
    assert prefix_tag("#Topics/Strategy", prefix) == "#Topics/Strategy"
    assert prefix_tag("Topics/Strategy", prefix) == "#Topics/Strategy"
    assert prefix_tag("#Entities/State/UK", "Entities") == "#Entities/State/UK"


def test_prefix_tag_normalization():
    assert prefix_tag("Nuclear Deterrence", "Topics") == "#Topics/Nuclear-Deterrence"
    assert prefix_tag("State/United Kingdom", "Entities") == "#Entities/State/United-Kingdom"


def test_prefix_tag_empty():
    assert prefix_tag("", "Topics") == ""
    assert prefix_tag(" ", "Topics") == ""


def test_prefix_tag_complex_hierarchy():
    tag = "Nuclear-Deterrence/Doctrine"
    assert prefix_tag(tag, "Topics") == "#Topics/Nuclear-Deterrence/Doctrine"
    assert prefix_tag("City/UK/London", "Entities") == "#Entities/City/UK/London"
