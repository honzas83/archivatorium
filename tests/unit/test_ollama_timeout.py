from unittest.mock import patch

from archivatorium.services.ollama_client import OllamaClient


def test_ollama_client_timeout_initialization():
    with patch("archivatorium.services.ollama_client.Client") as mock_client:
        OllamaClient(host="http://test:11434")
        # Verify it uses the default timeout of 300.0
        mock_client.assert_called_once_with(host="http://test:11434", timeout=300.0)


def test_ollama_client_timeout_override():
    with patch("archivatorium.services.ollama_client.Client") as mock_client:
        # We will add an option to override it if needed, or just check the constant
        from archivatorium.services import ollama_client

        original_timeout = ollama_client.OLLAMA_TIMEOUT
        ollama_client.OLLAMA_TIMEOUT = 10.0
        try:
            OllamaClient(host="http://test:11434")
            mock_client.assert_called_with(host="http://test:11434", timeout=10.0)
        finally:
            ollama_client.OLLAMA_TIMEOUT = original_timeout
