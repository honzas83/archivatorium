from archivatorium.utils.nlp import get_word_set, overlap_coefficient


def test_get_word_set() -> None:
    text = "The quick brown fox, jumps over the lazy dog."
    word_set = get_word_set(text)
    # Check some words (normalized to lowercase, punctuation removed)
    assert "the" in word_set
    assert "quick" in word_set
    assert "brown" in word_set
    assert "jumps" in word_set
    assert "lazy" in word_set
    assert "dog" in word_set
    # Case normalization
    assert "The" not in word_set


def test_overlap_coefficient_identical() -> None:
    s = frozenset(["a", "b", "c"])
    assert overlap_coefficient(s, s) == 1.0


def test_overlap_coefficient_different() -> None:
    s1 = frozenset(["a", "b"])
    s2 = frozenset(["c", "d"])
    assert overlap_coefficient(s1, s2) == 0.0


def test_overlap_coefficient_partial() -> None:
    s1 = get_word_set("The quick brown fox")
    s2 = get_word_set("The quick white fox")
    # 3 out of 4 words match: "The", "quick", "fox"
    expected_overlap = 0.75
    assert overlap_coefficient(s1, s2) == expected_overlap
