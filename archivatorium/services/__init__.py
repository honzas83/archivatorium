"""Shared service contracts."""

from archivatorium.services.llm_client import (
    CompletionState,
    GenerationOptions,
    LLMClient,
    LLMError,
    LLMErrorCategory,
    LLMTransport,
    ModelMessage,
    ModelRequest,
    ModelResponse,
    ProviderCapability,
    ReasoningDirective,
    StructuredLLMClient,
)
from archivatorium.services.llm_factory import (
    LLMCommand,
    ModelConnection,
    ProviderSelection,
    resolve_connection,
)

__all__ = [
    "CompletionState",
    "GenerationOptions",
    "LLMClient",
    "LLMCommand",
    "LLMError",
    "LLMErrorCategory",
    "LLMTransport",
    "ModelConnection",
    "ModelMessage",
    "ModelRequest",
    "ModelResponse",
    "ProviderCapability",
    "ProviderSelection",
    "ReasoningDirective",
    "StructuredLLMClient",
    "resolve_connection",
]
