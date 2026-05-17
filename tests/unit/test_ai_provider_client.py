import pytest
from unittest.mock import patch, MagicMock
from src.logic.ai_provider_client import AIProviderClient, AIProviderError
from src.services.ai_service import AiService


def test_chat_no_model():
    client = AIProviderClient(model="")
    with pytest.raises(AIProviderError, match="No AI model configured"):
        client.chat("hello")


def test_chat_calls_ai_service():
    client = AIProviderClient(host="http://localhost:11434", model="llama3")
    with patch.object(AiService, "generate", return_value="response text") as mock:
        result = client.chat("hello")
        assert result == "response text"
        mock.assert_called_once_with(
            "http://localhost:11434", "llama3", "hello"
        )


def test_chat_wraps_exception():
    client = AIProviderClient(model="llama3")
    with patch.object(AiService, "generate", side_effect=ConnectionError("refused")):
        with pytest.raises(AIProviderError, match="refused"):
            client.chat("hello")


def test_check_available_no_model():
    client = AIProviderClient(model="")
    msg = client.check_available()
    assert msg is not None
    assert "No AI model" in msg


def test_check_available_no_host():
    client = AIProviderClient(host="", model="llama3")
    msg = client.check_available()
    assert msg is not None
    assert "No AI host" in msg


def test_check_available_success():
    client = AIProviderClient(model="llama3")
    with patch.object(AiService, "list_models", return_value=[{"name": "llama3"}]) as mock:
        msg = client.check_available()
        assert msg is None
        mock.assert_called_once()


def test_check_available_no_models():
    client = AIProviderClient(model="llama3")
    with patch.object(AiService, "list_models", return_value=[]):
        msg = client.check_available()
        assert msg is not None
        assert "Cannot reach" in msg
