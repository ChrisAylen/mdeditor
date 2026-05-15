import pytest
from src.logic.editor_state import EditorState

def test_initial_state():
    state = EditorState()
    assert state.path is None
    assert state.content == ""
    assert state.is_dirty() is False

def test_set_path():
    state = EditorState()
    state.set_path("/path/to/file.md")
    assert state.path == "/path/to/file.md"

def test_set_content_marks_dirty():
    state = EditorState()
    state.set_content("Initial content")
    assert state.content == "Initial content"
    assert state.is_dirty() is True

def test_set_same_content_does_not_mark_dirty():
    state = EditorState()
    state.set_content("Initial content")
    state.mark_clean()
    
    state.set_content("Initial content")
    assert state.is_dirty() is False

def test_mark_clean():
    state = EditorState()
    state.set_content("Some content")
    assert state.is_dirty() is True
    
    state.mark_clean()
    assert state.is_dirty() is False

def test_is_dirty_transition():
    state = EditorState()
    assert state.is_dirty() is False
    
    state.set_content("Change 1")
    assert state.is_dirty() is True
    
    state.mark_clean()
    assert state.is_dirty() is False
    
    state.set_content("Change 2")
    assert state.is_dirty() is True
