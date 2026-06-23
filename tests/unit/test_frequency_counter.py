from archivatorium.utils.nlp import get_word_set, overlap_coefficient


def test_fuzzy_frequency_counting() -> None:
    # Simulate lines from different files
    l1 = "NATO SECRET - PRIVATE OFFICE"
    l2 = "NATO SECRET - PRIVAT OFFICE"  # OCR error

    s1 = get_word_set(l1)
    s2 = get_word_set(l2)

    assert overlap_coefficient(s1, s2) >= 0.75  # noqa: PLR2004
