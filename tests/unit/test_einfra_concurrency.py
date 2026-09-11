from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Event
from types import SimpleNamespace
from unittest.mock import MagicMock

from archivatorium.services.einfra_client import EinfraTransport
from archivatorium.services.llm_client import ModelMessage, ModelRequest


def test_parallel_first_images_share_one_capability_lookup(tmp_path: Path) -> None:
    images = [tmp_path / "one.png", tmp_path / "two.png"]
    for image in images:
        image.write_bytes(b"PNG")

    lookup_started = Event()
    release_lookup = Event()
    sdk = MagicMock()

    def list_models() -> SimpleNamespace:
        lookup_started.set()
        assert release_lookup.wait(timeout=2)
        return SimpleNamespace(data=[SimpleNamespace(id="qwen3.8-27b")])

    sdk.models.list.side_effect = list_models
    sdk.chat.completions.create.side_effect = lambda **_kwargs: iter(
        [
            SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        finish_reason="stop",
                        delta=SimpleNamespace(content="TEXT", reasoning_content=None),
                    )
                ]
            )
        ]
    )
    transport = EinfraTransport("secret", client=sdk)

    def generate(image: Path) -> str:
        request = ModelRequest(
            model="qwen3.8-27b",
            messages=(ModelMessage(role="user", text="ocr", images=(image,)),),
            delivery="incremental",
        )
        return transport.generate(request).visible_text

    with ThreadPoolExecutor(max_workers=2) as executor:
        first = executor.submit(generate, images[0])
        assert lookup_started.wait(timeout=2)
        second = executor.submit(generate, images[1])
        release_lookup.set()

    assert first.result() == "TEXT"
    assert second.result() == "TEXT"
    sdk.models.list.assert_called_once_with()
    assert sdk.chat.completions.create.call_count == 2
