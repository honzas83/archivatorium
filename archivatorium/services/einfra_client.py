"""OpenAI-compatible transport for the e-INFRA LLM service."""

from __future__ import annotations

import base64
import mimetypes
import time
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any

from openai import OpenAI

from archivatorium.services.llm_client import (
    CompletionState,
    LLMError,
    LLMErrorCategory,
    ModelRequest,
    ModelResponse,
    ProviderCapability,
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
        self._capabilities: dict[str, ProviderCapability] = {}

    def generate(self, request: ModelRequest) -> ModelResponse:
        if any(message.images for message in request.messages):
            self._validate_image_request(request)
        kwargs = self._build_request(request)
        return self._execute_with_retry(kwargs, request)

    def _build_request(self, request: ModelRequest) -> dict[str, Any]:
        messages: list[dict[str, Any]] = []
        for message in request.messages:
            if not message.images:
                messages.append({"role": message.role, "content": message.text})
                continue
            content: list[dict[str, Any]] = [{"type": "text", "text": message.text}]
            content.extend(
                {
                    "type": "image_url",
                    "image_url": {"url": self._image_data_url(image)},
                }
                for image in message.images
            )
            messages.append({"role": message.role, "content": content})
        kwargs: dict[str, Any] = {
            "model": request.model,
            "messages": messages,
            "stream": request.delivery == "incremental",
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

    def _execute_with_retry(
        self, kwargs: Mapping[str, Any], request: ModelRequest
    ) -> ModelResponse:
        for attempt in range(1, self._max_attempts + 1):
            try:
                response = self._client.chat.completions.create(**dict(kwargs))
                if request.delivery == "incremental":
                    return self._parse_stream(response, request.model)
                return self._parse_complete_response(response, request.model)
            except LLMError as error:
                if not error.retryable or attempt == self._max_attempts:
                    raise
                self._sleep(error.retry_after if error.retry_after is not None else float(attempt))
            except Exception as exc:
                normalized_error = self._normalize_sdk_error(exc, request.model)
                if not normalized_error.retryable or attempt == self._max_attempts:
                    raise normalized_error from exc
                retry_after = normalized_error.retry_after
                self._sleep(retry_after if retry_after is not None else float(attempt))
        raise AssertionError("unreachable retry state")

    def _validate_image_request(self, request: ModelRequest) -> None:
        capability = self._capabilities.get(request.model)
        if capability is None:
            capability = self._load_capability(request.model)
            self._capabilities[request.model] = capability
        if capability.multimodal is not True:
            raise LLMError(
                LLMErrorCategory.UNSUPPORTED_CAPABILITY,
                f"e-INFRA model {request.model} is not verified for multimodal OCR",
                retryable=False,
            )
        output_tokens = request.options.output_tokens or EINFRA_OCR_OUTPUT_TOKENS
        if (
            capability.maximum_output_tokens is not None
            and output_tokens > capability.maximum_output_tokens
        ):
            raise LLMError(
                LLMErrorCategory.CONFIGURATION,
                f"Requested output allowance exceeds the limit for e-INFRA model {request.model}",
                retryable=False,
            )

    def _load_capability(self, model: str) -> ProviderCapability:
        try:
            models = self._client.models.list()
        except Exception as exc:
            raise self._normalize_sdk_error(exc, model) from exc
        selected = next((item for item in models.data if getattr(item, "id", None) == model), None)
        if selected is None:
            raise LLMError(
                LLMErrorCategory.UNKNOWN_MODEL,
                f"e-INFRA model is unavailable: {model}",
                retryable=False,
            )
        if model == "qwen3.8-27b":
            multimodal: bool | None = True
            maximum_output = 32768
        else:
            capabilities = getattr(selected, "capabilities", None)
            multimodal = None
            maximum_output = None
            if isinstance(capabilities, Mapping):
                vision = capabilities.get("vision", capabilities.get("multimodal"))
                if isinstance(vision, bool):
                    multimodal = vision
                maximum = capabilities.get("maximum_output_tokens")
                if isinstance(maximum, int):
                    maximum_output = maximum
        return ProviderCapability(
            model=model,
            chat=True,
            multimodal=multimodal,
            structured_output=None,
            reasoning_efforts=frozenset({"none", "low", "medium", "high"}),
            maximum_output_tokens=maximum_output,
        )

    @staticmethod
    def _image_data_url(path: Path) -> str:
        try:
            encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        except OSError as exc:
            raise LLMError(
                LLMErrorCategory.CONFIGURATION,
                f"Unable to read OCR image: {path}",
                retryable=False,
            ) from exc
        mime_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        return f"data:{mime_type};base64,{encoded}"

    @staticmethod
    def _parse_stream(stream: Any, model: str) -> ModelResponse:
        visible_parts: list[str] = []
        finish_reason: str | None = None
        request_id: str | None = None
        for chunk in stream:
            request_id = getattr(chunk, "id", request_id)
            choices = getattr(chunk, "choices", [])
            if not choices:
                continue
            choice = choices[0]
            delta = getattr(choice, "delta", None)
            content = getattr(delta, "content", None)
            if content:
                visible_parts.append(content)
            chunk_finish = getattr(choice, "finish_reason", None)
            if chunk_finish is not None:
                finish_reason = chunk_finish
        if finish_reason == "length":
            raise LLMError(
                LLMErrorCategory.TRUNCATED,
                f"e-INFRA output for model {model} exhausted its token allowance",
                retryable=False,
                request_id=request_id,
            )
        if finish_reason is None:
            raise LLMError(
                LLMErrorCategory.INTERRUPTED,
                f"e-INFRA stream for model {model} ended before completion",
                retryable=True,
                request_id=request_id,
            )
        visible_text = "".join(visible_parts)
        if not visible_text:
            raise LLMError(
                LLMErrorCategory.EMPTY_RESPONSE,
                f"e-INFRA returned no visible output for model {model}",
                retryable=False,
                request_id=request_id,
            )
        return ModelResponse(
            visible_text=visible_text,
            finish_state=CompletionState.COMPLETE,
            provider_request_id=request_id,
        )

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
