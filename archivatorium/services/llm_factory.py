"""Resolve provider configuration before archival processing begins."""

from __future__ import annotations

import os
import stat
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Literal

from archivatorium.services.llm_client import (
    LLMClient,
    LLMError,
    LLMErrorCategory,
    StructuredLLMClient,
)

EINFRA_BASE_URL = "https://llm.ai.e-infra.cz/v1/"
EINFRA_DEFAULT_MODEL = "qwen3.8-27b"
OLLAMA_METADATA_MODEL = "gemma4:31b"
OLLAMA_OCR_MODEL = "qwen3.5:9b"
OLLAMA_OCR_DEFAULT_ENDPOINT = "http://localhost:11434"

type ProviderName = Literal["ollama", "e-infra"]


class LLMCommand(StrEnum):
    METADATA = "metadata"
    OCR = "ocr"


@dataclass(frozen=True, slots=True)
class ProviderSelection:
    command: LLMCommand
    provider: ProviderName = "ollama"
    endpoint_input: str | None = None
    legacy_host: str | None = None
    model_input: str | None = None
    credential_file: Path | None = None


@dataclass(frozen=True, slots=True)
class ModelConnection:
    provider: ProviderName
    command: LLMCommand
    endpoint: str | None
    model: str
    credential_source: Literal["environment", "file", "none"]
    secret: str | None = None

    def __repr__(self) -> str:
        return (
            "ModelConnection("
            f"provider={self.provider!r}, command={self.command!r}, endpoint={self.endpoint!r}, "
            f"model={self.model!r}, credential_source={self.credential_source!r}, "
            "secret=<redacted>)"
        )


def _configuration_error(message: str) -> LLMError:
    return LLMError(LLMErrorCategory.CONFIGURATION, message, retryable=False)


def _resolve_endpoint(selection: ProviderSelection, environ: Mapping[str, str]) -> str | None:
    endpoint = selection.endpoint_input
    legacy = selection.legacy_host
    if endpoint and legacy:
        left = endpoint.rstrip("/") if selection.provider == "e-infra" else endpoint
        right = legacy.rstrip("/") if selection.provider == "e-infra" else legacy
        if left != right:
            raise _configuration_error(
                "Conflicting endpoint values: --llm-base-url and --host must agree"
            )
    selected = endpoint or legacy
    if selected:
        return selected
    if selection.provider == "e-infra":
        return EINFRA_BASE_URL
    if selection.command is LLMCommand.OCR:
        return environ.get("OLLAMA_HOST") or OLLAMA_OCR_DEFAULT_ENDPOINT
    return None


def _read_credential_file(path: Path) -> str:
    try:
        file_stat = path.stat()
    except OSError as exc:
        raise _configuration_error(f"Unable to read e-INFRA credential file: {path}") from exc
    if not stat.S_ISREG(file_stat.st_mode):
        raise _configuration_error(f"e-INFRA credential path is not a regular file: {path}")
    if file_stat.st_mode & 0o077:
        raise _configuration_error(
            f"e-INFRA credential file must not be accessible by group or others: {path}"
        )
    try:
        secret = path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise _configuration_error(f"Unable to read e-INFRA credential file: {path}") from exc
    if not secret:
        raise _configuration_error(f"e-INFRA credential file is empty: {path}")
    return secret


def resolve_connection(
    selection: ProviderSelection,
    *,
    environ: Mapping[str, str] | None = None,
) -> ModelConnection:
    """Resolve one immutable connection without provider inference or fallback."""

    environment = os.environ if environ is None else environ
    endpoint = _resolve_endpoint(selection, environment)
    if selection.provider == "ollama":
        if selection.credential_file is not None:
            raise _configuration_error("--llm-api-key-file is only valid with e-infra")
        default_model = (
            OLLAMA_METADATA_MODEL if selection.command is LLMCommand.METADATA else OLLAMA_OCR_MODEL
        )
        return ModelConnection(
            provider="ollama",
            command=selection.command,
            endpoint=endpoint,
            model=selection.model_input or default_model,
            credential_source="none",
        )

    if selection.provider != "e-infra":
        raise _configuration_error(f"Unsupported LLM provider: {selection.provider}")
    if selection.credential_file is not None:
        secret = _read_credential_file(selection.credential_file)
        credential_source: Literal["environment", "file", "none"] = "file"
    else:
        secret = environment.get("E_INFRA_API_TOKEN", "").strip()
        credential_source = "environment"
        if not secret:
            raise _configuration_error("e-INFRA requires --llm-api-key-file or E_INFRA_API_TOKEN")
    return ModelConnection(
        provider="e-infra",
        command=selection.command,
        endpoint=endpoint,
        model=selection.model_input or EINFRA_DEFAULT_MODEL,
        credential_source=credential_source,
        secret=secret,
    )


def build_llm_client(
    connection: ModelConnection,
    *,
    ollama_client_factory: Callable[..., StructuredLLMClient] | None = None,
) -> StructuredLLMClient:
    """Construct exactly the selected provider; never fall back."""

    if connection.provider == "ollama":
        if ollama_client_factory is None:
            from archivatorium.services.ollama_client import OllamaClient

            ollama_client_factory = OllamaClient
        return ollama_client_factory(model=connection.model, host=connection.endpoint)

    from archivatorium.services.einfra_client import EinfraTransport

    if connection.secret is None or connection.endpoint is None:
        raise _configuration_error(
            "e-INFRA connection is missing validated credentials or endpoint"
        )
    return LLMClient(
        EinfraTransport(connection.secret, base_url=connection.endpoint),
        default_model=connection.model,
    )


def validate_ocr_configuration(
    connection: ModelConnection,
    *,
    mode: str,
    user: str | None = None,
    password: str | None = None,
    temperature: float | None = None,
    top_p: float | None = None,
    top_k: int | None = None,
    repeat_penalty: float | None = None,
    repeat_last_n: int | None = None,
    num_predict: int | None = None,
) -> None:
    """Reject explicit OCR semantics that e-INFRA cannot represent."""

    del temperature, top_p
    if connection.provider == "ollama":
        return
    if mode == "glm":
        raise _configuration_error("OCR mode glm is not supported by e-INFRA")
    incompatible = {
        "--user": user,
        "--password": password,
        "--top-k": top_k,
        "--repeat-penalty": repeat_penalty,
        "--repeat-last-n": repeat_last_n,
    }
    selected = [name for name, value in incompatible.items() if value is not None]
    if selected:
        raise _configuration_error(
            f"{', '.join(selected)} cannot be used with the e-INFRA provider"
        )
    if num_predict == -1:
        raise _configuration_error("--num-predict=-1 is not supported by e-INFRA")
