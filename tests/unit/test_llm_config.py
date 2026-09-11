from pathlib import Path

import pytest

from archivatorium.services.llm_client import LLMError, LLMErrorCategory
from archivatorium.services.llm_factory import (
    EINFRA_BASE_URL,
    EINFRA_DEFAULT_MODEL,
    OLLAMA_METADATA_MODEL,
    OLLAMA_OCR_MODEL,
    LLMCommand,
    ProviderSelection,
    resolve_connection,
)


@pytest.mark.parametrize(
    ("command", "expected_model", "expected_endpoint"),
    [
        (LLMCommand.METADATA, OLLAMA_METADATA_MODEL, None),
        (LLMCommand.OCR, OLLAMA_OCR_MODEL, "http://localhost:11434"),
    ],
)
def test_ollama_defaults_are_command_specific(
    command: LLMCommand, expected_model: str, expected_endpoint: str | None
) -> None:
    connection = resolve_connection(ProviderSelection(command=command), environ={})

    assert connection.provider == "ollama"
    assert connection.model == expected_model
    assert connection.endpoint == expected_endpoint
    assert connection.secret is None


@pytest.mark.parametrize("command", list(LLMCommand))
def test_einfra_defaults_are_shared(command: LLMCommand) -> None:
    connection = resolve_connection(
        ProviderSelection(provider="e-infra", command=command),
        environ={"E_INFRA_API_TOKEN": " token\n"},
    )

    assert connection.provider == "e-infra"
    assert connection.model == EINFRA_DEFAULT_MODEL
    assert connection.endpoint == EINFRA_BASE_URL
    assert connection.secret == "token"
    assert "token" not in repr(connection)


def test_explicit_model_and_endpoint_win() -> None:
    connection = resolve_connection(
        ProviderSelection(
            provider="e-infra",
            command=LLMCommand.METADATA,
            endpoint_input="https://example.test/v1",
            model_input="custom-model",
        ),
        environ={"E_INFRA_API_TOKEN": "secret"},
    )

    assert connection.model == "custom-model"
    assert connection.endpoint == "https://example.test/v1"


def test_matching_einfra_endpoint_aliases_allow_trailing_slash_difference() -> None:
    connection = resolve_connection(
        ProviderSelection(
            provider="e-infra",
            command=LLMCommand.OCR,
            endpoint_input="https://example.test/v1/",
            legacy_host="https://example.test/v1",
        ),
        environ={"E_INFRA_API_TOKEN": "secret"},
    )

    assert connection.endpoint == "https://example.test/v1/"


def test_conflicting_endpoint_aliases_fail_without_fallback() -> None:
    with pytest.raises(LLMError) as raised:
        resolve_connection(
            ProviderSelection(
                command=LLMCommand.METADATA,
                endpoint_input="http://one.test",
                legacy_host="http://two.test",
            ),
            environ={},
        )

    assert raised.value.category is LLMErrorCategory.CONFIGURATION
    assert "conflicting" in str(raised.value).lower()


def test_einfra_without_explicit_credential_fails() -> None:
    with pytest.raises(LLMError) as raised:
        resolve_connection(
            ProviderSelection(provider="e-infra", command=LLMCommand.METADATA), environ={}
        )

    assert raised.value.category is LLMErrorCategory.CONFIGURATION
    assert raised.value.retryable is False


def test_ollama_rejects_explicit_einfra_key_file(tmp_path: Path) -> None:
    with pytest.raises(LLMError, match="only valid with e-infra"):
        resolve_connection(
            ProviderSelection(
                command=LLMCommand.METADATA,
                credential_file=tmp_path / "key",
            ),
            environ={},
        )
