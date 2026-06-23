import unittest

from archivatorium.utils.metadata import extract_last_page_header, format_hierarchical_tag


class TestMetadataUtils(unittest.TestCase):
    def test_format_hierarchical_tag(self):
        cases = [
            ("Category A", "Topic A1", "#Category-A/Topic-A1"),
            (
                " Doctrine and Strategy ",
                " Nuclear Deterrence ",
                "#Doctrine-and-Strategy/Nuclear-Deterrence",
            ),
            (
                "Complex Name (With Parens)",
                "Topic!",
                "#Complex-Name-With-Parens/Topic",
            ),
        ]
        for cat, topic, expected in cases:
            with self.subTest(cat=cat, topic=topic):
                self.assertEqual(format_hierarchical_tag(cat, topic), expected)

    def test_extract_page_count_from_headers(self):
        content = """# Page 1
Some content
# Page 2
More content
# Page 5
Final content"""
        # We want it to count occurrences, so 3
        self.assertEqual(extract_last_page_header(content), 3)

    def test_extract_last_page_header_empty(self):
        self.assertIsNone(extract_last_page_header("No pages here"))
