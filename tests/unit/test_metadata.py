from archivatorium.data_model import PageMetadata
from archivatorium.utils.metadata import FileMetadataAnalyzer, extract_page_number


def test_extract_page_number_format_1() -> None:
    # Pattern: - X -
    assert extract_page_number("- 5 -") == 5  # noqa: PLR2004
    assert extract_page_number("  - 123 -  ") == 123  # noqa: PLR2004
    assert extract_page_number("- 1 -") == 1


def test_extract_page_number_format_2() -> None:
    # Pattern: -X-
    assert extract_page_number("-5-") == 5  # noqa: PLR2004
    assert extract_page_number("-123-") == 123  # noqa: PLR2004
    assert extract_page_number("-1-") == 1


def test_extract_page_number_format_tilde() -> None:
    # Pattern: ~ X ~ or ~X~
    assert extract_page_number("~ 5 ~") == 5  # noqa: PLR2004
    assert extract_page_number("~123~") == 123  # noqa: PLR2004
    assert extract_page_number(" ~ 1 ~ ") == 1


def test_extract_page_number_invalid() -> None:
    assert extract_page_number("Page 5") is None
    assert extract_page_number("- X -") is None
    assert extract_page_number("123") is None
    # This one actually matches in the current implementation because it's a search, not a full match
    assert extract_page_number("- 1 - some text") == 1


def test_file_metadata_analyzer_threshold() -> None:
    analyzer = FileMetadataAnalyzer(threshold=0.8)

    pages = []
    # 5 pages, 4 have "HEADER" and "FOOTER"
    for _ in range(4):
        p = PageMetadata(header_left=["HEADER"], footer_left=["FOOTER"])
        pages.append(p)

    pages.append(PageMetadata(header_left=["OTHER"], footer_left=["FOOTER"]))

    patterns = analyzer.analyze(pages)

    # "HEADER" should be in patterns (4/5 = 80%)
    # "FOOTER" should be in patterns (5/5 = 100%)
    assert frozenset(["HEADER"]) in patterns
    assert frozenset(["FOOTER"]) in patterns
    assert frozenset(["OTHER"]) not in patterns


def test_file_metadata_analyzer_below_threshold() -> None:
    analyzer = FileMetadataAnalyzer(threshold=0.8)

    pages = []
    # 5 pages, 3 have "HEADER" (60%)
    for _ in range(3):
        pages.append(PageMetadata(header_left=["HEADER"]))
    for _ in range(2):
        pages.append(PageMetadata(header_left=["OTHER"]))

    patterns = analyzer.analyze(pages)
    assert frozenset(["HEADER"]) not in patterns
