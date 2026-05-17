from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QScrollArea, QLabel, QFrame, QComboBox, QMessageBox,
    QSizePolicy, QApplication
)
from PySide6.QtCore import Qt, QThread, QSettings, Signal, QTimer
from src.logic.prompt_builder import PromptBuilder
from src.logic.conversation_service import ConversationService
from src.logic.ai_provider_client import AIProviderClient, AIProviderError
from src.ui.ai_worker import AiWorker


class _ChatBubble(QFrame):
    def __init__(self, role: str, content: str, parent=None):
        super().__init__(parent)
        self.role = role
        self.content = content
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(2)

        header = QLabel(self)
        if role == "user":
            header.setText("You")
            header.setStyleSheet("font-weight: bold; color: #2b6cb0;")
        else:
            header.setText("Assistant")
            header.setStyleSheet("font-weight: bold; color: #276749;")
        layout.addWidget(header)

        body = QLabel(content)
        body.setWordWrap(True)
        body.setTextInteractionFlags(
            Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard
        )
        body.setStyleSheet("padding: 4px 0;")
        layout.addWidget(body)

        self.action_layout = QHBoxLayout()
        self.action_layout.setSpacing(4)
        layout.addLayout(self.action_layout)

        border = "#e2e8f0"
        self.setStyleSheet(
            f"_ChatBubble {{ border: 1px solid {border}; border-radius: 4px; "
            f"margin: 2px 0; }}"
        )

    def add_action(self, label: str, callback):
        btn = QPushButton(label)
        btn.setFixedHeight(22)
        btn.setStyleSheet(
            "font-size: 11px; padding: 0 8px;"
        )
        btn.clicked.connect(callback)
        self.action_layout.addWidget(btn)


class AIChatPanel(QWidget):
    insert_text_requested = Signal(str)
    replace_selection_requested = Signal(str)
    copy_text_requested = Signal(str)

    CONTEXT_MODES = {
        "Selected Text": PromptBuilder.CONTEXT_SELECTED,
        "Current Document": PromptBuilder.CONTEXT_DOCUMENT,
        "None": PromptBuilder.CONTEXT_NONE,
    }

    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.conversation = ConversationService()
        self._pending_thread = None
        self._pending_worker = None

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        header = QLabel("AI Chat")
        header.setStyleSheet("font-size: 14px; font-weight: bold; padding: 4px 0;")
        layout.addWidget(header)

        cm_layout = QHBoxLayout()
        cm_layout.addWidget(QLabel("Context:"))
        self.context_combo = QComboBox()
        for label in self.CONTEXT_MODES:
            self.context_combo.addItem(label)
        cm_layout.addWidget(self.context_combo, 1)
        layout.addLayout(cm_layout)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.msg_container = QWidget()
        self.msg_layout = QVBoxLayout(self.msg_container)
        self.msg_layout.setAlignment(Qt.AlignTop)
        self.msg_layout.setSpacing(6)

        self.empty_label = QLabel(
            "Ask the AI to improve, summarise, explain, "
            "or transform your markdown."
        )
        self.empty_label.setWordWrap(True)
        self.empty_label.setStyleSheet("color: #718096; padding: 20px 8px;")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.msg_layout.addWidget(self.empty_label)

        self.msg_layout.addStretch()
        self.scroll.setWidget(self.msg_container)
        layout.addWidget(self.scroll, 1)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #718096; font-size: 12px;")
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)

        self.input_edit = QTextEdit()
        self.input_edit.setPlaceholderText("Type a message…")
        self.input_edit.setMaximumHeight(80)
        self.input_edit.setAcceptRichText(False)
        layout.addWidget(self.input_edit)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.send_btn = QPushButton("Send")
        self.send_btn.setFixedWidth(80)
        btn_layout.addWidget(self.send_btn)
        layout.addLayout(btn_layout)

        self.input_edit.textChanged.connect(self._on_input_changed)
        self.send_btn.clicked.connect(self._on_send)

    def _get_ai_settings(self):
        settings = QSettings("mdeditor", "mdeditor")
        host = settings.value("ai/host", "http://localhost:11434")
        model = settings.value("ai/model", "")
        return host, model

    def _on_input_changed(self):
        text = self.input_edit.toPlainText()
        has_text = bool(text.strip())
        self.send_btn.setEnabled(has_text and not self.conversation.is_waiting)

    def _on_send(self):
        user_text = self.input_edit.toPlainText().strip()
        if not user_text or self.conversation.is_waiting:
            return

        host, model = self._get_ai_settings()
        if not model:
            QMessageBox.warning(
                self,
                "AI Not Configured",
                "No AI model configured. Please set one in AI > Settings.",
            )
            return

        context_label = self.context_combo.currentText()
        context_mode = self.CONTEXT_MODES.get(context_label, PromptBuilder.CONTEXT_NONE)

        selected_text = None
        full_document = None
        if context_mode == PromptBuilder.CONTEXT_SELECTED:
            from PySide6.QtWidgets import QApplication
            focus = QApplication.focusWidget()
            if focus and hasattr(focus, "textCursor") and hasattr(focus, "toPlainText"):
                cursor = focus.textCursor()
                if cursor.hasSelection():
                    selected_text = cursor.selectedText()
            if not selected_text:
                QMessageBox.information(
                    self, "No Selection",
                    "Select text in the editor first, or switch context mode."
                )
                return
        elif context_mode == PromptBuilder.CONTEXT_DOCUMENT:
            full_document = self.controller.state.content

        self.conversation.add_user_message(user_text, context_mode=context_mode)
        self._rebuild_messages()

        history = [m.to_dict() for m in self.conversation.messages[:-1]]
        prompt = PromptBuilder.build(
            user_prompt=user_text,
            context_mode=context_mode,
            selected_text=selected_text,
            full_document=full_document,
            history=history,
        )

        self._send_prompt(host, model, prompt)

    def _send_prompt(self, host: str, model: str, prompt: str):
        self._set_waiting(True)

        self._pending_thread = QThread()
        self._pending_worker = AiWorker(host, model, prompt)
        self._pending_worker.moveToThread(self._pending_thread)
        self._pending_thread.started.connect(self._pending_worker.run)
        self._pending_worker.finished.connect(self._on_response)
        self._pending_worker.error.connect(self._on_error)
        self._pending_worker.finished.connect(self._pending_thread.quit)
        self._pending_worker.finished.connect(self._pending_worker.deleteLater)
        self._pending_worker.error.connect(self._pending_thread.quit)
        self._pending_worker.error.connect(self._pending_worker.deleteLater)
        self._pending_thread.finished.connect(self._pending_thread.deleteLater)
        self._pending_thread.finished.connect(self._on_thread_done)
        self._pending_thread.start()

    def _on_response(self, content: str):
        self.conversation.add_assistant_message(content)
        self._rebuild_messages()
        self._set_waiting(False)

    def _on_error(self, error_msg: str):
        self.status_label.setText(f"Error: {error_msg}")
        self.status_label.setStyleSheet("color: #e53e3e; font-size: 12px;")
        self.status_label.setVisible(True)
        self._set_waiting(False)

    def _on_thread_done(self):
        self._pending_thread = None
        self._pending_worker = None

    def _set_waiting(self, waiting: bool):
        self.send_btn.setEnabled(not waiting)
        self.input_edit.setEnabled(not waiting)
        if waiting:
            self.status_label.setText("Generating…")
            self.status_label.setStyleSheet("color: #718096; font-size: 12px;")
            self.status_label.setVisible(True)
        else:
            self.status_label.setVisible(False)
        self._on_input_changed()

    def _rebuild_messages(self):
        for i in reversed(range(self.msg_layout.count())):
            item = self.msg_layout.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()

        self.empty_label = None

        has_messages = False
        for msg in self.conversation.messages:
            has_messages = True
            bubble = _ChatBubble(msg.role, msg.content)
            if msg.role == "assistant":
                bubble.add_action("Insert", lambda c=msg.content: self._on_insert(c))
                bubble.add_action("Replace", lambda c=msg.content: self._on_replace(c))
                bubble.add_action("Copy", lambda c=msg.content: self._on_copy(c))
            self.msg_layout.addWidget(bubble)

        if not has_messages:
            self.empty_label = QLabel(
                "Ask the AI to improve, summarise, explain, "
                "or transform your markdown."
            )
            self.empty_label.setWordWrap(True)
            self.empty_label.setStyleSheet("color: #718096; padding: 20px 8px;")
            self.empty_label.setAlignment(Qt.AlignCenter)
            self.msg_layout.addWidget(self.empty_label)

        self.msg_layout.addStretch()

        QTimer.singleShot(50, self._scroll_to_bottom)

    def _scroll_to_bottom(self):
        scrollbar = self.scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _on_insert(self, text: str):
        self.insert_text_requested.emit(text)

    def _on_replace(self, text: str):
        self.replace_selection_requested.emit(text)

    def _on_copy(self, text: str):
        QApplication.clipboard().setText(text)
        self.status_label.setText("Copied to clipboard")
        self.status_label.setStyleSheet("color: #38a169; font-size: 12px;")
        self.status_label.setVisible(True)
        QTimer.singleShot(2000, lambda: self.status_label.setVisible(False))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and not (event.modifiers() & Qt.ShiftModifier):
            if self.send_btn.isEnabled():
                self._on_send()
            return
        super().keyPressEvent(event)
