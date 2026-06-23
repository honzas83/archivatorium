from pathlib import Path

from archivatorium.utils.files import get_filtered_path


def test_get_filtered_path() -> None:
    out = Path("output/doc.md")
    filtered = get_filtered_path(out)
    assert filtered == Path("output/doc.md.filtered.md")


def test_get_filtered_path_subdir() -> None:
    out = Path("output/sub/doc.md")
    filtered = get_filtered_path(out)
    assert filtered == Path("output/sub/doc.md.filtered.md")
