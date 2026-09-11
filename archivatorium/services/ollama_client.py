"""Native Ollama transport and backward-compatible structured facade."""

from __future__ import annotations

from typing import Any, TypeVar

from ollama import Client
from pydantic import BaseModel

from archivatorium.services.llm_client import (
    CompletionState,
    LLMClient,
    ModelRequest,
    ModelResponse,
)

T = TypeVar("T", bound=BaseModel)

OLLAMA_TIMEOUT = 300.0


class OllamaTransport:
    """Translate shared requests to the established native Ollama chat API."""

    provider = "ollama"

    def __init__(self, client: Any) -> None:
        self.client = client

    def generate(self, request: ModelRequest) -> ModelResponse:
        messages: list[dict[str, Any]] = []
        for message in request.messages:
            native_message: dict[str, Any] = {"role": message.role, "content": message.text}
            if message.images:
                native_message["images"] = [str(image) for image in message.images]
            messages.append(native_message)

        options: dict[str, int | float] = {}
        if request.options.context_tokens is not None:
            options["num_ctx"] = request.options.context_tokens
        for shared_name, native_name in (
            ("temperature", "temperature"),
            ("top_p", "top_p"),
            ("top_k", "top_k"),
            ("repeat_penalty", "repeat_penalty"),
            ("repeat_last_n", "repeat_last_n"),
            ("output_tokens", "num_predict"),
        ):
            value = getattr(request.options, shared_name)
            if value is not None:
                options[native_name] = value

        kwargs: dict[str, Any] = {"model": request.model, "messages": messages}
        if request.structured_result is not None:
            kwargs["format"] = request.structured_result.json_schema
        if options:
            kwargs["options"] = options
        if request.structured_result is None:
            kwargs["stream"] = False
        if request.reasoning.mode == "disabled":
            kwargs["think"] = False
        elif request.reasoning.mode == "effort":
            kwargs["think"] = request.reasoning.level

        response = self.client.chat(**kwargs)
        if request.structured_result is not None:
            content = response["message"]["content"]
        else:
            content = getattr(response, "message", {}).get("content", "")
            if not content and isinstance(response, dict):
                content = response.get("message", {}).get("content", "")
        return ModelResponse(
            visible_text=content or "",
            finish_state=CompletionState.COMPLETE,
        )


class OllamaClient:
    """Historical structured-client API retained for existing callers."""

    def __init__(self, model: str = "gemma4:26b", host: str | None = None):
        self.model = model
        self.client = Client(host=host, timeout=OLLAMA_TIMEOUT)

    @property
    def provider(self) -> str:
        return "ollama"

    def extract_structured(
        self,
        prompt: str,
        schema: type[T],
        retries: int = 3,
        model: str | None = None,
        **kwargs: Any,
    ) -> T:
        facade = LLMClient(OllamaTransport(self.client), self.model)
        return facade.extract_structured(
            prompt,
            schema,
            retries=retries,
            model=model,
            **kwargs,
        )
