import pytest

from archivatorium.utils.person_entities import normalize_person_path


@pytest.mark.parametrize(
    ("raw_path", "expected"),
    [
        ("Person/Andrae/K-W", "Person/Andrae/K-W"),
        ("Person/Andrae/K. W.", "Person/Andrae/K-W"),
        ("Person/Luns/Joseph M.A.H.", "Person/Luns/Joseph-M-A-H"),
        ("Person/Luns/Joseph", "Person/Luns/Joseph"),
        ("Person/Andrae", "Person/Andrae"),
        ("Person/Van Der Waals/Johannes Diderik", "Person/Van-Der-Waals/Johannes-Diderik"),
        ("Person/Picard/Jean-Luc", "Person/Picard/Jean-Luc"),
    ],
)
def test_normalize_person_path(raw_path: str, expected: str) -> None:
    assert normalize_person_path(raw_path) == expected


def test_role_only_given_component_is_removed() -> None:
    assert normalize_person_path("Person/Andrae/Minister") == "Person/Andrae"
    assert normalize_person_path("Person/Luns/Secretary-General") == "Person/Luns"


@pytest.mark.parametrize(
    "raw_path",
    [
        "Person",
        "Person//Joseph",
        "Person/Minister",
        "Person/Andrae/K-W/Minister",
        "Org/NATO",
    ],
)
def test_invalid_person_path_is_rejected(raw_path: str) -> None:
    assert normalize_person_path(raw_path) is None
