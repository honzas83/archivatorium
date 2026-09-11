"""Minimal synthetic e-INFRA checks; never part of the default test run."""

import os
from pathlib import Path
from typing import cast

import pytest
from PIL import Image, ImageDraw
from pydantic import BaseModel

from archivatorium.ocr_engine import OCREngine
from archivatorium.services.llm_client import LLMClient
from archivatorium.services.llm_factory import (
    LLMCommand,
    ProviderSelection,
    build_llm_client,
    resolve_connection,
)

pytestmark = [
    pytest.mark.live_einfra,
    pytest.mark.skipif(
        os.environ.get("ARCHIVATORIUM_RUN_EINFRA_LIVE") != "1",
        reason="set ARCHIVATORIUM_RUN_EINFRA_LIVE=1 to enable e-INFRA calls",
    ),
]


class _LivePayload(BaseModel):
    answer: str


def _live_client(command: LLMCommand) -> LLMClient:
    connection = resolve_connection(ProviderSelection(provider="e-infra", command=command))
    return cast(LLMClient, build_llm_client(connection))


def test_live_einfra_structured_response() -> None:
    client = _live_client(LLMCommand.METADATA)

    result = client.extract_structured(
        "Return the word ready in the answer field.",
        _LivePayload,
        retries=0,
        think="low",
    )

    assert result.answer.strip()


def test_live_einfra_short_ocr_and_local_resume(tmp_path: Path) -> None:
    source = tmp_path / "synthetic.pdf"
    output = tmp_path / "synthetic.md"
    image = Image.new("RGB", (640, 160), "white")
    ImageDraw.Draw(image).text((30, 60), "ARCHIVATORIUM LIVE OCR 42", fill="black")
    image.save(source, "PDF", resolution=72)

    client = _live_client(LLMCommand.OCR)
    engine = OCREngine(
        model="qwen3.8-27b",
        mode="qwen38",
        dpi=72,
        model_think="low",
        llm_client=client,
    )
    first = engine.run_ocr(source, output)
    assert first.strip()
    assert engine.last_run_attempted_pages == 1

    second = engine.run_ocr(source, output)
    assert second == first
    assert engine.last_run_attempted_pages == 0
