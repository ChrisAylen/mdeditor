from PySide6.QtCore import QObject, Signal
from src.services.ai_service import AiService


class AiWorker(QObject):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, host: str, model: str, prompt: str, parent=None):
        super().__init__(parent)
        self.host = host
        self.model = model
        self.prompt = prompt

    def run(self):
        try:
            result = AiService.generate(self.host, self.model, self.prompt)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
