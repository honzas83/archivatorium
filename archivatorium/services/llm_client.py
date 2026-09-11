"""Provider-neutral model access contracts and structured extraction."""

from __future__ import annotations

import json
import logging
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any, Literal, Protocol, TypeVar, cast, runtime_checkable

from pydantic import BaseModel, ValidationError

from archivatorium.utils.model_think import ModelThink

T = TypeVar("T", bound=BaseModel)

logger = logging.getLogger(__name__)

STRUCTURED_SYSTEM_INSTRUCTION = (
    "You are a specialized metadata extraction assistant. "
    "Extract requested fields accurately and respond "
    "strictly in JSON format matching the schema."
)


class CompletionState(StrEnum):
    """Normalized terminal state of a model response."""

    COMPLETE = "complete"
    LENGTH = "length"
    INTERRUPTED = "interrupted"
    FAILED = "failed"


class LLMErrorCategory(StrEnum):
    """Safe provider-independent failure categories."""

    CONFIGURATION = "configuration"
    AUTHENTICATION = "authentication"
    PERMISSION = "permission"
    INVALID_REQUEST = "invalid_request"
    UNKNOWN_MODEL = "unknown_model"
    UNSUPPORTED_CAPABILITY = "unsupported_capability"
    RATE_LIMITED = "rate_limited"
    TRANSIENT = "transient"
    TRUNCATED = "truncated"
    EMPTY_RESPONSE = "empty_response"
    INTERRUPTED = "interrupted"
    VALIDATION = "validation"


class LLMError(RuntimeError):
    """A normalized error whose message is safe to display."""

    def __init__(
        self,
        category: LLMErrorCategory,
        message: str,
        *,
        retryable: bool,
        retry_after: float | None = None,
        request_id: str | None = None,
    ) -> None:
        super().__init__(message)
        self.category = category
        self.retryable = retryable
        self.retry_after = retry_after
        self.request_id = request_id


@dataclass(frozen=True, slots=True)
class ReasoningDirective:
    """Distinguish omitted reasoning from explicitly disabled reasoning."""

    mode: Literal["omitted", "disabled", "effort"] = "omitted"
    level: Literal["low", "medium", "high"] | None = None

    def __post_init__(self) -> None:
        if (self.mode == "effort") != (self.level is not None):
            raise ValueError("reasoning effort requires exactly one named level")

    @classmethod
    def omitted(cls) -> ReasoningDirective:
        return cls()

    @classmethod
    def disabled(cls) -> ReasoningDirective:
        return cls(mode="disabled")

    @classmethod
    def effort(cls, level: Literal["low", "medium", "high"]) -> ReasoningDirective:
        return cls(mode="effort", level=level)

    @classmethod
    def from_model_think(cls, value: ModelThink | None) -> ReasoningDirective:
        if value is None:
            return cls.omitted()
        if value is False:
            return cls.disabled()
        return cls.effort(value)


@dataclass(frozen=True, slots=True)
class ModelMessage:
    role: Literal["system", "user"]
    text: str
    images: tuple[Path, ...] = ()


@dataclass(frozen=True, slots=True)
class GenerationOptions:
    temperature: float | None = None
    top_p: float | None = None
    top_k: int | None = None
    repeat_penalty: float | None = None
    repeat_last_n: int | None = None
    output_tokens: int | None = None
    context_tokens: int | None = None
    explicit_fields: frozenset[str] = field(default_factory=frozenset)

    def __post_init__(self) -> None:
        if self.temperature is not None and self.temperature < 0:
            raise ValueError("temperature must be greater than or equal to 0")
        if self.top_p is not None and not 0 <= self.top_p <= 1:
            raise ValueError("top_p must be between 0 and 1")
        if self.top_k is not None and self.top_k < 0:
            raise ValueError("top_k must be greater than or equal to 0")
        if self.repeat_penalty is not None and self.repeat_penalty <= 0:
            raise ValueError("repeat_penalty must be greater than 0")
        if self.repeat_last_n is not None and self.repeat_last_n < -1:
            raise ValueError("repeat_last_n must be greater than or equal to -1")
        if self.output_tokens is not None and self.output_tokens != -1 and self.output_tokens < 1:
            raise ValueError("output_tokens must be -1 or greater than or equal to 1")
        if self.context_tokens is not None and self.context_tokens < 1:
            raise ValueError("context_tokens must be greater than or equal to 1")


@dataclass(frozen=True, slots=True)
class StructuredResultContract:
    schema_name: str
    json_schema: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class ModelRequest:
    model: str
    messages: tuple[ModelMessage, ...]
    options: GenerationOptions = field(default_factory=GenerationOptions)
    reasoning: ReasoningDirective = field(default_factory=ReasoningDirective.omitted)
    structured_result: StructuredResultContract | None = None
    delivery: Literal["complete", "incremental"] = "complete"

    def __post_init__(self) -> None:
        if not self.model:
            raise ValueError("model must not be empty")
        if not self.messages:
            raise ValueError("at least one model message is required")


@dataclass(frozen=True, slots=True)
class ModelResponse:
    visible_text: str
    finish_state: CompletionState
    usage: Mapping[str, int] | None = None
    provider_request_id: str | None = None


@dataclass(frozen=True, slots=True)
class ProviderCapability:
    model: str
    chat: bool
    multimodal: bool | None
    structured_output: bool | None
    reasoning_efforts: frozenset[str]
    maximum_output_tokens: int | None


@runtime_checkable
class LLMTransport(Protocol):
    provider: str

    def generate(self, request: ModelRequest) -> ModelResponse:
        """Translate and execute one immutable provider-neutral request."""


@runtime_checkable
class StructuredLLMClient(Protocol):
    def extract_structured(
        self,
        prompt: str,
        schema: type[T],
        retries: int = 3,
        model: str | None = None,
        **kwargs: Any,
    ) -> T:
        """Return a response validated against ``schema``."""


class LLMClient:
    """Application-facing facade shared by structured and text workflows."""

    def __init__(self, transport: LLMTransport, default_model: str) -> None:
        self.transport = transport
        self.default_model = default_model

    @property
    def provider(self) -> str:
        return self.transport.provider

    def generate_text(self, request: ModelRequest) -> ModelResponse:
        return self.transport.generate(request)

    def extract_structured(
        self,
        prompt: str,
        schema: type[T],
        retries: int = 3,
        model: str | None = None,
        **kwargs: Any,
    ) -> T:
        """Preserve the historical structured prompt and validation retry contract."""

        think = cast(ModelThink | None, kwargs.pop("think", None))
        if kwargs:
            names = ", ".join(sorted(kwargs))
            raise TypeError(f"Unsupported structured request options: {names}")

        attempt = 0
        current_prompt = prompt
        last_error: ValidationError | None = None
        json_schema = schema.model_json_schema()
        while attempt <= retries:
            request = ModelRequest(
                model=model or self.default_model,
                messages=(
                    ModelMessage(role="system", text=STRUCTURED_SYSTEM_INSTRUCTION),
                    ModelMessage(
                        role="user",
                        text=(
                            f"{current_prompt}\n\nStrictly follow this JSON schema:\n"
                            f"{json.dumps(json_schema, indent=2)}"
                        ),
                    ),
                ),
                options=GenerationOptions(temperature=0),
                reasoning=ReasoningDirective.from_model_think(think),
                structured_result=StructuredResultContract(
                    schema_name=schema.__name__, json_schema=json_schema
                ),
            )
            response = self.transport.generate(request)
            content = response.visible_text.strip()
            if content.startswith("```"):
                content = re.sub(r"^```(?:json)?\s*", "", content)
                content = re.sub(r"\s*```$", "", content)
            try:
                return schema.model_validate_json(content)
            except ValidationError as exc:
                attempt += 1
                last_error = exc
                logger.warning("Schema validation failed on attempt %d: %s", attempt, exc)
                if attempt <= retries:
                    current_prompt += (
                        f"\n\nIMPORTANT: Previous response failed validation: {exc}. "
                        "Please ensure the output strictly matches the schema."
                    )

        logger.error("Failed extraction after %d attempts.", retries + 1)
        if last_error is not None:
            raise last_error
        raise RuntimeError("Extraction failed")
