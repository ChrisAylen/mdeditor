import sys
from PySide6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.controller.app_controller import AppController
from src.logic.editor_state import EditorState
from src.services.file_service import FileService

def main():
    app = QApplication(sys.argv)
    
    # Initialize core components
    state = EditorState()
    file_service = FileService()
    controller = AppController(state, file_service)
    
    window = MainWindow(controller)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
