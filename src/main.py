import sys
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.controller.app_controller import AppController
from src.logic.editor_state import EditorState
from src.logic.save_state_manager import SaveStateManager
from src.services.file_service import FileService
from src.services.recovery_service import RecoveryService

def main():
    app = QApplication(sys.argv)
    app.setOrganizationName("mdeditor")
    app.setApplicationName("mdeditor")

    state = EditorState()
    file_service = FileService()
    recovery_service = RecoveryService()
    save_state_manager = SaveStateManager()
    controller = AppController(state, file_service, recovery_service, save_state_manager)

    window = MainWindow(controller)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
