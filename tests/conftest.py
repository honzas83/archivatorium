from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from ocrpolish.models.metadata import AggregatedTaggingResult, MetadataSchema, TopicResult
from tests.unit.test_ollama_client import create_mock_ollama_response


@pytest.fixture
def hierarchy_file(tmp_path: Path) -> Path:
    path = tmp_path / "hierarchy.yaml"
    path.write_text(
        """
categories:
  - category: Defence Policy
    description: Defence policy matters
    topics:
      - topic: Nuclear Planning
        description: Nuclear planning documents
        positive_samples: nuclear planning group
        negative_samples: routine agenda
""".lstrip(),
        encoding="utf-8",
    )
    return path


@pytest.fixture
def useful_tags_file(tmp_path: Path) -> Path:
    path = tmp_path / "useful_tags.yaml"
    path.write_text(
        """
useful_tags:
  - Nuclear Planning
  - NATO
  - Ministerial Guidance
""".lstrip(),
        encoding="utf-8",
    )
    return path


@pytest.fixture
def metadata_response_factory() -> Callable[..., Any]:
    def factory(**overrides: Any) -> Any:
        data = {
            "title": "Test Document",
            "summary": "This is a test document.",
            "abstract": "This is a detailed test abstract.",
            "language": "English",
            "date": "1981-11-19",
            "archive_code": "TEST-1",
        }
        data.update(overrides)
        return create_mock_ollama_response(MetadataSchema(**data).model_dump_json())

    return factory


@pytest.fixture
def tagging_result() -> AggregatedTaggingResult:
    return AggregatedTaggingResult(
        conceptual_tags=["NATO"],
        entity_tags=["Org/NATO"],
        topic_tags=[
            TopicResult(
                topic="Defence Policy/Nuclear Planning",
                reason='The text mentions "nuclear planning group".',
            )
        ],
    )


@pytest.fixture
def mixed_vault_factory(tmp_path: Path) -> Callable[[], Path]:
    def factory() -> Path:
        vault = tmp_path / "vault"
        vault.mkdir()
        (vault / "doc.md").write_text("# Document\n#Tags/Document-Only\n", encoding="utf-8")
        (vault / "Index - Tags.md").write_text("#Tags/Index-Only\n", encoding="utf-8")
        (vault / "index.md").write_text("#Tags/Landing-Only\n", encoding="utf-8")
        (vault / "doc.filtered.md").write_text("#Tags/Sidecar-Only\n", encoding="utf-8")
        templates = vault / "templates"
        templates.mkdir()
        (templates / "template.md").write_text("#Tags/Template-Only\n", encoding="utf-8")
        hidden = vault / ".obsidian"
        hidden.mkdir()
        (hidden / "support.md").write_text("#Tags/Hidden-Only\n", encoding="utf-8")
        return vault

    return factory


@pytest.fixture
def substantive_text() -> str:
    return (
        "The NATO Nuclear Planning Group discussed nuclear release procedures, "
        "consultation procedures, deterrence strategy, WINTEX 71 exercises, "
        "SACEUR command arrangements, and operational doctrine."
    )


@pytest.fixture
def administrative_stub_text() -> str:
    return "This document is incorporated into the initial document and cancelled."


@pytest.fixture
def assert_filesystem_unchanged() -> Callable[[Path, dict[str, tuple[bool, bytes]]], None]:
    def snapshot(root: Path) -> dict[str, tuple[bool, bytes]]:
        paths = {root}
        if root.exists():
            paths.update(root.rglob("*"))
        return {
            str(path.relative_to(root) if path != root else Path(".")): (
                path.is_file(),
                path.read_bytes() if path.is_file() else b"",
            )
            for path in sorted(paths)
        }

    def assert_unchanged(root: Path, before: dict[str, tuple[bool, bytes]]) -> None:
        assert snapshot(root) == before

    assert_unchanged.snapshot = snapshot  # type: ignore[attr-defined]
    return assert_unchanged
