from ocrpolish.utils.nlp import filter_low_value_tags, normalize_exercise_tag, to_title_case_custom


def test_normalize_exercise_tag():
    assert normalize_exercise_tag("Wintex-71") == "WINTEX/71"
    assert normalize_exercise_tag("Wintex 71") == "WINTEX/71"
    assert normalize_exercise_tag("WINTEX 1971") == "WINTEX/71"
    assert normalize_exercise_tag("FALLEX-66") == "FALLEX/66"
    assert normalize_exercise_tag("other-tag") == "other-tag"

def test_filter_low_value_tags():
    tags = ["#Report", "#Important", "#Study", "#Agenda", "#Notice", "#ValidTag"]
    filtered = filter_low_value_tags(tags)
    assert "#Report" not in filtered
    assert "#Study" not in filtered
    assert "#Agenda" not in filtered
    assert "#Notice" not in filtered
    assert "#Important" in filtered
    assert "#ValidTag" in filtered

def test_to_title_case_custom():
    assert to_title_case_custom("NUCLEAR DETERRENCE") == "NUCLEAR DETERRENCE"
    assert to_title_case_custom("nato strategy") == "Nato Strategy"
    assert to_title_case_custom("united kingdom") == "United Kingdom"
    assert to_title_case_custom("NATO strategy") == "NATO Strategy"
