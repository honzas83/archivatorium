from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from pydantic import BaseModel

from archivatorium.services.einfra_client import EinfraTransport
from archivatorium.services.llm_client import (
    CompletionState,
    GenerationOptions,
    LLMClient,
    LLMError,
    LLMErrorCategory,
    ModelMessage,
    ModelRequest,
    ReasoningDirective,
    StructuredResultContract,
)


class _Payload(BaseModel):
    value: str


def _completion(content: str | None, finish_reason: str = "stop") -> SimpleNamespace:
    return SimpleNamespace(
        id="request-safe",
        choices=[
            SimpleNamespace(
                finish_reason=finish_reason,
                message=SimpleNamespace(content=content, reasoning_content="PRIVATE"),
            )
        ],
        usage=SimpleNamespace(prompt_tokens=10, completion_tokens=20, total_tokens=30),
    )


def test_structured_request_uses_json_schema_and_reasoning_mapping() -> None:
    sdk = MagicMock()
    sdk.chat.completions.create.return_value = _completion('{"value":"ok"}')
    transport = EinfraTransport("secret", client=sdk)
    client = LLMClient(transport, default_model="qwen3.8-27b")

    result = client.extract_structured("prompt", _Payload, retries=0, think=False)

    assert result.value == "ok"
    kwargs = sdk.chat.completions.create.call_args.kwargs
    assert kwargs["model"] == "qwen3.8-27b"
    assert kwargs["reasoning_effort"] == "none"
    assert kwargs["max_completion_tokens"] == 8192
    assert kwargs["temperature"] == 0
    assert kwargs["response_format"] == {
        "type": "json_schema",
        "json_schema": {
            "name": "_Payload",
            "schema": _Payload.model_json_schema(),
            "strict": True,
        },
    }
    assert kwargs["stream"] is False


@pytest.mark.parametrize(
    ("directive", "expected"),
    [
        (ReasoningDirective.disabled(), "none"),
        (ReasoningDirective.effort("low"), "low"),
        (ReasoningDirective.effort("medium"), "medium"),
        (ReasoningDirective.effort("high"), "high"),
    ],
)
def test_reasoning_mapping(directive: ReasoningDirective, expected: str) -> None:
    sdk = MagicMock()
    sdk.chat.completions.create.return_value = _completion("visible")
    request = ModelRequest(
        model="qwen3.8-27b",
        messages=(ModelMessage(role="user", text="prompt"),),
        reasoning=directive,
    )

    response = EinfraTransport("secret", client=sdk).generate(request)

    assert response.visible_text == "visible"
    assert sdk.chat.completions.create.call_args.kwargs["reasoning_effort"] == expected


def test_omitted_reasoning_does_not_send_provider_field() -> None:
    sdk = MagicMock()
    sdk.chat.completions.create.return_value = _completion("visible")
    request = ModelRequest(
        model="qwen3.8-27b",
        messages=(ModelMessage(role="user", text="prompt"),),
    )

    EinfraTransport("secret", client=sdk).generate(request)

    assert "reasoning_effort" not in sdk.chat.completions.create.call_args.kwargs


@pytest.mark.parametrize(
    ("content", "finish_reason", "category"),
    [
        ("partial", "length", LLMErrorCategory.TRUNCATED),
        (None, "stop", LLMErrorCategory.EMPTY_RESPONSE),
        ("", "stop", LLMErrorCategory.EMPTY_RESPONSE),
    ],
)
def test_incomplete_or_empty_response_is_never_success(
    content: str | None, finish_reason: str, category: LLMErrorCategory
) -> None:
    sdk = MagicMock()
    sdk.chat.completions.create.return_value = _completion(content, finish_reason)
    request = ModelRequest(
        model="qwen3.8-27b",
        messages=(ModelMessage(role="user", text="prompt"),),
    )

    with pytest.raises(LLMError) as raised:
        EinfraTransport("secret", client=sdk).generate(request)

    assert raised.value.category is category


def test_safe_transient_failure_retries_identical_request() -> None:
    sdk = MagicMock()
    error = RuntimeError("temporary secret-bearing provider detail")
    error.status_code = 503  # type: ignore[attr-defined]
    sdk.chat.completions.create.side_effect = [error, _completion("visible")]
    sleep = MagicMock()
    request = ModelRequest(
        model="qwen3.8-27b",
        messages=(ModelMessage(role="user", text="prompt"),),
        options=GenerationOptions(output_tokens=99),
    )

    response = EinfraTransport("secret", client=sdk, sleep=sleep).generate(request)

    assert response.finish_state is CompletionState.COMPLETE
    assert sdk.chat.completions.create.call_count == 2
    assert (
        sdk.chat.completions.create.call_args_list[0]
        == sdk.chat.completions.create.call_args_list[1]
    )
    sleep.assert_called_once_with(1.0)


def test_authentication_failure_is_permanent_and_redacted() -> None:
    sdk = MagicMock()
    error = RuntimeError("Authorization: Bearer secret-token")
    error.status_code = 401  # type: ignore[attr-defined]
    sdk.chat.completions.create.side_effect = error
    request = ModelRequest(
        model="qwen3.8-27b",
        messages=(ModelMessage(role="user", text="prompt"),),
        structured_result=StructuredResultContract("payload", {}),
    )

    with pytest.raises(LLMError) as raised:
        EinfraTransport("secret-token", client=sdk).generate(request)

    assert raised.value.category is LLMErrorCategory.AUTHENTICATION
    assert raised.value.retryable is False
    assert "secret-token" not in str(raised.value)
    sdk.chat.completions.create.assert_called_once()
