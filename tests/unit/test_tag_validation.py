import logging

from ocrpolish.utils.tag_parser import CanonicalTagParser


class ListHandler(logging.Handler):
    """A custom logging handler that stores captured log records."""

    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


def test_malformed_entity_type() -> None:
    handler = ListHandler()
    logger = logging.getLogger("ocrpolish.utils.tag_parser")
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)

    try:
        text = "#Entities/Country/France"
        parser = CanonicalTagParser()
        tags = parser.parse_text(text)

        assert "Entities/Country/France" not in tags.raw_paths
        assert not tags.entities["State"]
        assert any("Unsupported entity type: Country" in r.getMessage() for r in handler.records)
    finally:
        logger.removeHandler(handler)


def test_malformed_city_tag() -> None:
    handler = ListHandler()
    logger = logging.getLogger("ocrpolish.utils.tag_parser")
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)

    try:
        text = "#Entities/City/London"
        parser = CanonicalTagParser()
        tags = parser.parse_text(text)

        assert not tags.entities["City"]
        assert any(
            "City tag must have format #Entities/City/<State>/<City>" in r.getMessage()
            for r in handler.records
        )
    finally:
        logger.removeHandler(handler)


def test_malformed_state_tag() -> None:
    handler = ListHandler()
    logger = logging.getLogger("ocrpolish.utils.tag_parser")
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)

    try:
        text = "#Entities/State/US/East"
        parser = CanonicalTagParser()
        tags = parser.parse_text(text)

        assert not tags.entities["State"]
        assert any(
            "State tag must have format #Entities/State/<Name>" in r.getMessage()
            for r in handler.records
        )
    finally:
        logger.removeHandler(handler)


def test_hierarchical_conceptual_tag_is_valid() -> None:
    handler = ListHandler()
    logger = logging.getLogger("ocrpolish.utils.tag_parser")
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)

    try:
        text = "#Tags/Deterrence/Nuclear"
        parser = CanonicalTagParser()
        tags = parser.parse_text(text)

        assert tags.conceptual_tags == {"deterrence/nuclear"}
        assert not handler.records
    finally:
        logger.removeHandler(handler)
