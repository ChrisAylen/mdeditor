import pytest
from unittest.mock import MagicMock
from src.controller.app_controller import AppController
from src.logic.editor_state import EditorState
from src.services.file_service import FileService

@pytest.fixture
def mock_file_service():
    return MagicMock(spec=FileService)

@pytest.fixture
def editor_state():
    return EditorState()

@pytest.fixture
def controller(mock_file_service, editor_state):
    return AppController(editor_state, mock_file_service)

def test_open_file(controller, mock_file_service, editor_state):
    # Arrange
    test_path = "test.md"
    test_content = "Hello World"
    mock_file_service.read_file.return_value = test_content
    
    # Act
    controller.open_file(test_path)
    
    # Assert
    mock_file_service.read_file.assert_called_once_with(test_path)
    assert editor_state.path == test_path
    assert editor_state.content == test_content
    assert editor_state.is_dirty() is False

def test_save_current_file_success(controller, mock_file_service, editor_state):
    # Arrange
    test_path = "test.md"
    test_content = "Updated content"
    editor_state.set_path(test_path)
    editor_state.set_content(test_content)
    
    mock_file_service.write_file.return_value = True
    
    # Act
    result = controller.save_current_file()
    
    # Assert
    assert result is True
    mock_file_service.write_file.assert_called_once_with(test_path, test_content)
    assert editor_state.is_dirty() is False

def test_save_current_file_no_path(controller, editor_state):
    # Arrange
    editor_state.set_path(None)
    
    # Act
    result = controller.save_current_file()
    
    # Assert
    assert result is False

def test_save_current_file_failure(controller, mock_file_service, editor_state):
    # Arrange
    test_path = "test.md"
    test_content = "Updated content"
    editor_state.set_path(test_path)
    editor_state.set_content(test_content)
    
    mock_file_service.write_file.return_value = False
    
    # Act
    result = controller.save_current_file()
    
    # Assert
    assert result is False
    assert editor_state.is_dirty() is True

def test_save_file_as_success(controller, mock_file_service, editor_state):
    # Arrange
    test_content = "New file content"
    editor_state.set_content(test_content)
    new_path = "new_file.md"
    mock_file_service.write_file.return_value = True
    
    # Act
    result = controller.save_file_as(new_path)
    
    # Assert
    assert result is True
    mock_file_service.write_file.assert_called_once_with(new_path, test_content)
    assert editor_state.path == new_path
    assert editor_state.is_dirty() is False

def test_create_new_file(controller, editor_state):
    # Arrange
    editor_state.set_path("existing.md")
    editor_state.set_content("some content")
    editor_state.mark_dirty()
    
    # Act
    controller.create_new_file()
    
    # Assert
    assert editor_state.path is None
    assert editor_state.content == ""
    assert editor_state.is_dirty() is False
