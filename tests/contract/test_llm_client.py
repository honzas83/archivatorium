from collections.abc import Iterable
from pathlib import Path

import pytest
from pydantic import BaseModel

from archivatorium.services.llm_client import (
    CompletionState,
    GenerationOptions,
    LLMClient,
    LLMError,
    LLMErrorCategory,
    ModelMessage,
    ModelRequest,
    ModelResponse,
    ReasoningDirective,
)


class _Result(BaseModel):
    value: str


class _FakeTransport:
    provider = "e-infra"

    def __init__(self, responses: Iterable[ModelResponse | Exception]) -> None:
        self.responses = iter(responses)
        self.requests: list[ModelRequest] = []

    def generate(self, request: ModelRequest) -> ModelResponse:
        self.requests.append(request)
        response = next(self.responses)
        if isinstance(response, Exception):
            raise response
        return response


def test_generate_text_passes_immutable_request_and_visible_response() -> None:
    expected = ModelResponse(visible_text="visible", finish_state=CompletionState.COMPLETE)
    transport = _FakeTransport([expected])
    client = LLMClient(transport, default_model="model")
    request = ModelRequest(
        model="model",
        messages=(ModelMessage(role="user", text="prompt", images=(Path("page.png"),)),),
        options=GenerationOptions(output_tokens=32),
        reasoning=ReasoningDirective.disabled(),
    )

    assert client.generate_text(request) == expected
    assert transport.requests == [request]


def test_extract_structured_builds_existing_prompt_and_validates() -> None:
    transport = _FakeTransport(
        [ModelResponse(visible_text='{"value":"ok"}', finish_state=CompletionState.COMPLETE)]
    )
    client = LLMClient(transport, default_model="default")

    result = client.extract_structured("original", _Result, retries=0, think="low")

    assert result == _Result(value="ok")
    request = transport.requests[0]
    assert request.model == "default"
    assert request.reasoning == ReasoningDirective.effort("low")
    assert request.options.temperature == 0
    assert request.structured_result is not None
    assert request.messages[0].text == (
        "You are a specialized metadata extraction assistant. "
        "Extract requested fields accurately and respond strictly in JSON format matching the schema."
    )
    assert request.messages[1].text.startswith(
        'original\n\nStrictly follow this JSON schema:\n{\n  "properties"'
    )


def test_extract_structured_retries_only_validation_and_keeps_semantics() -> None:
    transport = _FakeTransport(
        [
            ModelResponse(visible_text="[]", finish_state=CompletionState.COMPLETE),
            ModelResponse(
                visible_text='```json\n{"value":"fixed"}\n```',
                finish_state=CompletionState.COMPLETE,
            ),
        ]
    )
    client = LLMClient(transport, default_model="default")

    result = client.extract_structured(
        "original", _Result, retries=1, model="override", think=False
    )

    assert result.value == "fixed"
    assert len(transport.requests) == 2
    first, second = transport.requests
    assert first.model == second.model == "override"
    assert first.reasoning == second.reasoning == ReasoningDirective.disabled()
    assert first.options == second.options
    assert "IMPORTANT: Previous response failed validation:" not in first.messages[1].text
    assert "IMPORTANT: Previous response failed validation:" in second.messages[1].text


def test_transport_error_is_not_converted_to_validation_retry() -> None:
    error = LLMError(LLMErrorCategory.AUTHENTICATION, "Authentication failed", retryable=False)
    transport = _FakeTransport([error])
    client = LLMClient(transport, default_model="default")

    with pytest.raises(LLMError) as raised:
        client.extract_structured("original", _Result, retries=3)

    assert raised.value is error
    assert len(transport.requests) == 1
