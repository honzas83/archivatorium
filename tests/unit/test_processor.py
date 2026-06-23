from archivatorium.processor import is_structural_marker


def test_is_structural_marker() -> None:
    assert is_structural_marker("# Page 3") is True
    assert is_structural_marker("-1-") is True
    assert is_structural_marker("Normal text") is False
    assert is_structural_marker("") is False
