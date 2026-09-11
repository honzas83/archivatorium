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
    build_llm_client,
    resolve_connection,
    validate_ocr_configuration,
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
    "build_llm_client",
    "resolve_connection",
    "validate_ocr_configuration",
]
