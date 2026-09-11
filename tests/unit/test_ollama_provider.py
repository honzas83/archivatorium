import json
from unittest.mock import MagicMock, patch

import pytest
from pydantic import BaseModel

from archivatorium.services.ollama_client import OLLAMA_TIMEOUT, OllamaClient


class _Payload(BaseModel):
    value: str


def test_structured_client_preserves_native_constructor_and_complete_request() -> None:
    with patch("archivatorium.services.ollama_client.Client") as client_class:
        native = client_class.return_value
        native.chat.return_value = {"message": {"content": '{"value":"ok"}'}}
        client = OllamaClient(model="chosen", host=None)

        result = client.extract_structured("prompt", _Payload, think=False)

    assert result == _Payload(value="ok")
    client_class.assert_called_once_with(host=None, timeout=OLLAMA_TIMEOUT)
    native.chat.assert_called_once_with(
        model="chosen",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a specialized metadata extraction assistant. "
                    "Extract requested fields accurately and respond "
                    "strictly in JSON format matching the schema."
                ),
            },
            {
                "role": "user",
                "content": (
                    "prompt\n\nStrictly follow this JSON schema:\n"
                    f"{json.dumps(_Payload.model_json_schema(), indent=2)}"
                ),
            },
        ],
        format=_Payload.model_json_schema(),
        options={"temperature": 0},
        think=False,
    )


def test_structured_validation_retry_accumulates_only_corrective_prompt() -> None:
    client = OllamaClient.__new__(OllamaClient)
    client.model = "chosen"
    client.client = MagicMock()
    client.client.chat.side_effect = [
        {"message": {"content": "[]"}},
        {"message": {"content": "{}"}},
        {"message": {"content": '{"value":"ok"}'}},
    ]

    result = client.extract_structured("prompt", _Payload, retries=2, think="high")

    assert result.value == "ok"
    calls = client.client.chat.call_args_list
    assert len(calls) == 3
    assert [call.kwargs["think"] for call in calls] == ["high", "high", "high"]
    assert [call.kwargs["model"] for call in calls] == ["chosen", "chosen", "chosen"]
    prompts = [call.kwargs["messages"][1]["content"] for call in calls]
    assert prompts[0].count("IMPORTANT: Previous response failed validation:") == 0
    assert prompts[1].count("IMPORTANT: Previous response failed validation:") == 1
    assert prompts[2].count("IMPORTANT: Previous response failed validation:") == 2


def test_non_validation_exception_is_not_retried() -> None:
    client = OllamaClient.__new__(OllamaClient)
    client.model = "chosen"
    client.client = MagicMock()
    client.client.chat.side_effect = RuntimeError("offline")

    with pytest.raises(RuntimeError, match="offline"):
        client.extract_structured("prompt", _Payload, retries=3)

    client.client.chat.assert_called_once()
