import pytest
from unittest.mock import MagicMock
from src.controller.app_controller import AppController
from src.logic.editor_state import EditorState
from src.logic.save_state_manager import SaveStateManager
from src.services.file_service import FileService
from src.services.recovery_service import RecoveryService


@pytest.fixture
def mock_file_service():
    return MagicMock(spec=FileService)


@pytest.fixture
def mock_recovery_service():
    return MagicMock(spec=RecoveryService)


@pytest.fixture
def editor_state():
    return EditorState()


@pytest.fixture
def controller(mock_file_service, mock_recovery_service, editor_state):
    return AppController(editor_state, mock_file_service, mock_recovery_service)


def test_open_file(controller, mock_file_service, editor_state):
    test_path = "test.md"
    test_content = "Hello World"
    mock_file_service.read_file.return_value = test_content

    controller.open_file(test_path)

    mock_file_service.read_file.assert_called_once_with(test_path)
    assert editor_state.path == test_path
    assert editor_state.content == test_content
    assert editor_state.is_dirty() is False


def test_save_current_file_success(controller, mock_file_service, editor_state, mock_recovery_service):
    test_path = "test.md"
    test_content = "Updated content"
    editor_state.set_path(test_path)
    editor_state.set_content(test_content)
    mock_file_service.write_file.return_value = True

    result = controller.save_current_file()

    assert result is True
    mock_file_service.write_file.assert_called_once_with(test_path, test_content)
    assert editor_state.is_dirty() is False
    mock_recovery_service.clear_recovery.assert_called_once_with(editor_state.doc_id)


def test_save_current_file_no_path(controller, editor_state):
    editor_state.set_path(None)
    result = controller.save_current_file()
    assert result is False


def test_save_current_file_failure(controller, mock_file_service, editor_state):
    test_path = "test.md"
    test_content = "Updated content"
    editor_state.set_path(test_path)
    editor_state.set_content(test_content)
    mock_file_service.write_file.return_value = False

    result = controller.save_current_file()

    assert result is False
    assert editor_state.is_dirty() is True
    assert controller.save_state_manager.last_error is not None


def test_save_file_as_success(controller, mock_file_service, editor_state, mock_recovery_service):
    test_content = "New file content"
    editor_state.set_content(test_content)
    new_path = "new_file.md"
    mock_file_service.write_file.return_value = True

    result = controller.save_file_as(new_path)

    assert result is True
    mock_file_service.write_file.assert_called_once_with(new_path, test_content)
    assert editor_state.path == new_path
    assert editor_state.is_dirty() is False
    mock_recovery_service.clear_recovery.assert_called_once_with(editor_state.doc_id)


def test_create_new_file(controller, editor_state):
    editor_state.set_path("existing.md")
    editor_state.set_content("some content")
    editor_state.mark_dirty()

    controller.create_new_file()

    assert editor_state.path is None
    assert editor_state.content == ""
    assert editor_state.is_dirty() is False


def test_save_recovery(controller, mock_recovery_service, editor_state):
    editor_state.set_content("recovery content")
    mock_recovery_service.save_recovery.return_value = True

    result = controller.save_recovery()

    assert result is True
    mock_recovery_service.save_recovery.assert_called_once_with(
        content="recovery content",
        original_path=None,
        doc_id=editor_state.doc_id,
    )


def test_has_recovery(controller, mock_recovery_service):
    mock_recovery_service.has_recoveries.return_value = True
    assert controller.has_recovery() is True


def test_list_recoveries(controller, mock_recovery_service):
    mock_recovery_service.list_recoveries.return_value = [{"doc_id": "abc"}]
    assert controller.list_recoveries() == [{"doc_id": "abc"}]


def test_recover_content(controller, mock_recovery_service):
    mock_recovery_service.load_recovery.return_value = "recovered text"
    result = controller.recover_content("doc1")
    assert result == "recovered text"
    mock_recovery_service.load_recovery.assert_called_once_with("doc1")


def test_discard_recovery(controller, mock_recovery_service):
    controller.discard_recovery("doc1")
    mock_recovery_service.clear_recovery.assert_called_once_with("doc1")
