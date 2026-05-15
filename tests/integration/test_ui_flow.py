import pytest
from PySide6.QtWidgets import QApplication, QTextEdit
from src.ui.main_window import MainWindow
from src.ui.menu_bar import MenuBar
from src.controller.app_controller import AppController
from src.logic.editor_state import EditorState
from src.services.file_service import FileService

@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app

def test_main_window_initialization(qapp):
    state = EditorState()
    file_service = FileService()
    controller = AppController(state, file_service)
    window = MainWindow(controller)
    assert "Simple Markdown Editor" in window.windowTitle()
    assert window.centralWidget() is not None
    assert isinstance(window.centralWidget(), QTextEdit)

def test_menu_bar_actions(qapp):
    state = EditorState()
    file_service = FileService()
    controller = AppController(state, file_service)
    window = MainWindow(controller)
    menu_bar = window.menu_bar
    assert menu_bar.file_menu is not None
    assert menu_bar.action_new is not None
    assert menu_bar.action_open is not None
    assert menu_bar.action_save is not None
    assert menu_bar.action_save_as is not None
    assert menu_bar.action_exit is not None

