"""OpenAI-compatible transport for the e-INFRA LLM service."""

from __future__ import annotations

import time
from collections.abc import Callable, Mapping
from typing import Any

from openai import OpenAI

from archivatorium.services.llm_client import (
    CompletionState,
    LLMError,
    LLMErrorCategory,
    ModelRequest,
    ModelResponse,
)

EINFRA_STRUCTURED_OUTPUT_TOKENS = 8192
EINFRA_OCR_OUTPUT_TOKENS = 16384
EINFRA_REQUEST_TIMEOUT = 300.0


class EinfraTransport:
    """Translate shared requests to e-INFRA Chat Completions."""

    provider = "e-infra"

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = "https://llm.ai.e-infra.cz/v1/",
        client: Any | None = None,
        max_attempts: int = 3,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self._client = client or OpenAI(
            api_key=api_key,
            base_url=base_url,
            max_retries=0,
            timeout=EINFRA_REQUEST_TIMEOUT,
        )
        self._max_attempts = max_attempts
        self._sleep = sleep

    def generate(self, request: ModelRequest) -> ModelResponse:
        kwargs = self._build_request(request)
        response = self._call_with_retry(kwargs, request.model)
        return self._parse_complete_response(response, request.model)

    def _build_request(self, request: ModelRequest) -> dict[str, Any]:
        messages: list[dict[str, Any]] = [
            {"role": message.role, "content": message.text} for message in request.messages
        ]
        kwargs: dict[str, Any] = {
            "model": request.model,
            "messages": messages,
            "stream": False,
        }
        if request.reasoning.mode == "disabled":
            kwargs["reasoning_effort"] = "none"
        elif request.reasoning.mode == "effort":
            kwargs["reasoning_effort"] = request.reasoning.level
        if request.options.temperature is not None:
            kwargs["temperature"] = request.options.temperature
        if request.options.top_p is not None:
            kwargs["top_p"] = request.options.top_p

        output_tokens = request.options.output_tokens
        if request.structured_result is not None:
            kwargs["response_format"] = {
                "type": "json_schema",
                "json_schema": {
                    "name": request.structured_result.schema_name,
                    "schema": request.structured_result.json_schema,
                    "strict": True,
                },
            }
            output_tokens = output_tokens or EINFRA_STRUCTURED_OUTPUT_TOKENS
        elif request.delivery == "incremental":
            output_tokens = output_tokens or EINFRA_OCR_OUTPUT_TOKENS
        if output_tokens is not None:
            kwargs["max_completion_tokens"] = output_tokens
        return kwargs

    def _call_with_retry(self, kwargs: Mapping[str, Any], model: str) -> Any:
        for attempt in range(1, self._max_attempts + 1):
            try:
                return self._client.chat.completions.create(**dict(kwargs))
            except Exception as exc:
                error = self._normalize_sdk_error(exc, model)
                if not error.retryable or attempt == self._max_attempts:
                    raise error from exc
                self._sleep(error.retry_after if error.retry_after is not None else float(attempt))
        raise AssertionError("unreachable retry state")

    @staticmethod
    def _normalize_sdk_error(exc: Exception, model: str) -> LLMError:
        status = getattr(exc, "status_code", None)
        request_id = getattr(exc, "request_id", None)
        if status == 401:
            category = LLMErrorCategory.AUTHENTICATION
            retryable = False
        elif status == 403:
            category = LLMErrorCategory.PERMISSION
            retryable = False
        elif status == 404:
            category = LLMErrorCategory.UNKNOWN_MODEL
            retryable = False
        elif status == 429:
            category = LLMErrorCategory.RATE_LIMITED
            retryable = True
        elif isinstance(status, int) and status >= 500:
            category = LLMErrorCategory.TRANSIENT
            retryable = True
        elif status is not None:
            category = LLMErrorCategory.INVALID_REQUEST
            retryable = False
        else:
            name = type(exc).__name__.lower()
            retryable = any(token in name for token in ("timeout", "connection"))
            category = LLMErrorCategory.TRANSIENT if retryable else LLMErrorCategory.INVALID_REQUEST
        retry_after = EinfraTransport._retry_after(exc) if retryable else None
        status_text = f" (HTTP {status})" if status is not None else ""
        return LLMError(
            category,
            f"e-INFRA request for model {model} failed: {category.value}{status_text}",
            retryable=retryable,
            retry_after=retry_after,
            request_id=request_id,
        )

    @staticmethod
    def _retry_after(exc: Exception) -> float | None:
        response = getattr(exc, "response", None)
        headers = getattr(response, "headers", None) or getattr(exc, "headers", None)
        if headers is None:
            return None
        value = headers.get("retry-after") or headers.get("Retry-After")
        try:
            return min(max(float(value), 0.0), 30.0)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _parse_complete_response(response: Any, model: str) -> ModelResponse:
        choice = response.choices[0]
        finish_reason = getattr(choice, "finish_reason", None)
        if finish_reason == "length":
            raise LLMError(
                LLMErrorCategory.TRUNCATED,
                f"e-INFRA output for model {model} exhausted its token allowance",
                retryable=False,
                request_id=getattr(response, "id", None),
            )
        content = getattr(choice.message, "content", None)
        if not content:
            raise LLMError(
                LLMErrorCategory.EMPTY_RESPONSE,
                f"e-INFRA returned no visible output for model {model}",
                retryable=False,
                request_id=getattr(response, "id", None),
            )
        usage_object = getattr(response, "usage", None)
        usage = None
        if usage_object is not None:
            usage = {
                name: value
                for name in ("prompt_tokens", "completion_tokens", "total_tokens")
                if isinstance((value := getattr(usage_object, name, None)), int)
            }
        return ModelResponse(
            visible_text=content,
            finish_state=CompletionState.COMPLETE,
            usage=usage,
            provider_request_id=getattr(response, "id", None),
        )
