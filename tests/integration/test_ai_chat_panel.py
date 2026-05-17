import pytest
from unittest.mock import patch, MagicMock
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication
from src.logic.editor_state import EditorState
from src.logic.save_state_manager import SaveStateManager
from src.services.file_service import FileService
from src.services.recovery_service import RecoveryService
from src.controller.app_controller import AppController
from src.ui.ai_chat_panel import AIChatPanel
from src.logic.prompt_builder import PromptBuilder


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    app.setOrganizationName("mdeditor_test")
    app.setApplicationName("mdeditor_test")
    return app


@pytest.fixture
def controller():
    state = EditorState()
    file_service = FileService()
    recovery_service = MagicMock(spec=RecoveryService)
    save_state_manager = SaveStateManager()
    return AppController(state, file_service, recovery_service, save_state_manager)


@pytest.fixture
def panel(qapp, controller, monkeypatch):
    settings = QSettings("mdeditor_test", "mdeditor_test")
    settings.setValue("ai/host", "http://localhost:11434")
    settings.setValue("ai/model", "llama3")
    return AIChatPanel(controller)


def test_initial_state(panel):
    assert panel.send_btn.isEnabled() is False
    assert panel.cancel_btn.isVisible() is False
    assert panel.input_edit.toPlainText() == ""
    assert panel.conversation.is_waiting is False
    assert panel.context_combo.currentText() == "Selected Text"


def test_input_enables_send(qtbot, panel):
    qtbot.keyClicks(panel.input_edit, "Hello")
    assert panel.send_btn.isEnabled() is True


def test_empty_input_disables_send(qtbot, panel):
    qtbot.keyClicks(panel.input_edit, "   ")
    assert panel.send_btn.isEnabled() is False


@pytest.mark.parametrize("mode", ["Selected Text", "Current Document", "None"])
def test_context_modes_available(panel, mode):
    idx = panel.context_combo.findText(mode)
    assert idx >= 0, f"Mode '{mode}' not found in combo"


def test_send_adds_user_message(qtbot, panel):
    with (
        patch("src.ui.ai_chat_panel.AiWorker") as mock_worker,
        patch.object(panel, "_on_send") as mock_send,
    ):
        mock_instance = mock_worker.return_value
        mock_instance.finished = MagicMock()
        mock_instance.error = MagicMock()

        panel.conversation.add_user_message("Summarise this")
        assert len(panel.conversation.messages) == 1
        assert panel.conversation.messages[0].role == "user"


def test_cancel_button_appears_on_wait(panel):
    panel._set_waiting(True)
    assert panel.cancel_btn.isHidden() is False
    assert panel.send_btn.isHidden() is True
    assert panel.input_edit.isEnabled() is False


def test_cancel_button_hidden_when_not_waiting(panel):
    panel._set_waiting(True)
    panel._set_waiting(False)
    assert panel.cancel_btn.isHidden() is True
    assert panel.send_btn.isHidden() is False
    assert panel.input_edit.isEnabled() is True


def test_rebuild_messages_creates_bubbles(qtbot, panel):
    panel.conversation.add_user_message("Hi", context_mode="none")
    panel.conversation.add_assistant_message("Hello there")
    panel._rebuild_messages()
    qtbot.wait(100)

    bubble_count = 0
    for i in range(panel.msg_layout.count()):
        item = panel.msg_layout.itemAt(i)
        if item and item.widget() and "ChatBubble" in type(item.widget()).__name__:
            bubble_count += 1
    assert bubble_count == 2


def test_clear_conversation(panel):
    panel.conversation.add_user_message("Hi")
    panel.conversation.add_assistant_message("Hello")
    assert len(panel.conversation.messages) == 2
    panel.conversation.clear()
    assert len(panel.conversation.messages) == 0


def test_friendly_error_messages():
    assert "Cannot reach Ollama" in AIChatPanel._friendly_error("Connection refused")
    assert "Cannot reach Ollama" in AIChatPanel._friendly_error("Errno 111")
    assert "timed out" in AIChatPanel._friendly_error("timed out")
    assert "Model not found" in AIChatPanel._friendly_error("model not found")
    assert "AI request failed: foo" == AIChatPanel._friendly_error("foo")
