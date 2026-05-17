import pytest
from src.ui.ai_chat_panel import AIChatPanel


class TestFriendlyError:
    def test_connection_refused(self):
        msg = AIChatPanel._friendly_error("Connection refused")
        assert "Cannot reach Ollama" in msg

    def test_connection_refused_errno(self):
        msg = AIChatPanel._friendly_error("Errno 111 connecting")
        assert "Cannot reach Ollama" in msg

    def test_timeout(self):
        msg = AIChatPanel._friendly_error("timed out")
        assert "timed out" in msg

    def test_model_not_found(self):
        msg = AIChatPanel._friendly_error("model 'llama3' not found")
        assert "Model not found" in msg

    def test_generic_error(self):
        msg = AIChatPanel._friendly_error("something else went wrong")
        assert "AI request failed" in msg
        assert "something else" in msg
