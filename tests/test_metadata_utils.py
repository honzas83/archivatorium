import unittest

from ocrpolish.utils.metadata import format_hierarchical_tag


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
                "#Complex-Name-(With-Parens)/Topic!",
            ),
        ]
        for cat, topic, expected in cases:
            with self.subTest(cat=cat, topic=topic):
                self.assertEqual(format_hierarchical_tag(cat, topic), expected)
