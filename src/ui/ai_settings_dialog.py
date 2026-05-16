from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QMessageBox
)
from PySide6.QtCore import QSettings
from src.services.ai_service import AiService


class AiSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AI Settings")
        self.setMinimumWidth(450)
        self.settings = QSettings("mdeditor", "mdeditor")
        self._setup_ui()
        self._load_settings()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # Host
        host_layout = QHBoxLayout()
        host_layout.addWidget(QLabel("Ollama Host:"))
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("http://localhost:11434")
        host_layout.addWidget(self.host_input)
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh_models)
        host_layout.addWidget(refresh_btn)
        layout.addLayout(host_layout)

        # Model
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Model:"))
        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        self.model_combo.setPlaceholderText("Select or type a model name")
        model_layout.addWidget(self.model_combo)
        layout.addLayout(model_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._save_settings)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def _load_settings(self):
        host = self.settings.value("ai/host", "http://localhost:11434")
        self.host_input.setText(host)
        self._refresh_models()

    def _refresh_models(self):
        host = self.host_input.text().strip() or "http://localhost:11434"
        self.model_combo.clear()
        self.model_combo.addItem("")  # allow empty selection
        models = AiService.list_models(host)
        model_names = [m["name"] for m in models]
        self.model_combo.addItems(model_names)

        saved_model = self.settings.value("ai/model", "")
        if saved_model in model_names:
            self.model_combo.setCurrentText(saved_model)
        elif saved_model:
            self.model_combo.setCurrentText(saved_model)

    def _save_settings(self):
        host = self.host_input.text().strip()
        model = self.model_combo.currentText().strip()
        if not host:
            QMessageBox.warning(self, "Warning", "Ollama host is required.")
            return
        self.settings.setValue("ai/host", host)
        self.settings.setValue("ai/model", model)
        self.settings.sync()
        self.accept()

    @staticmethod
    def get_settings():
        settings = QSettings("mdeditor", "mdeditor")
        return {
            "host": settings.value("ai/host", "http://localhost:11434"),
            "model": settings.value("ai/model", ""),
        }
