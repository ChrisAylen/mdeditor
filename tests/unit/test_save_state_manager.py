import pytest
from src.logic.save_state_manager import SaveStateManager


def test_initial_state_saved():
    mgr = SaveStateManager()
    assert mgr.status_text(False) == "Saved"


def test_initial_state_unsaved():
    mgr = SaveStateManager()
    assert mgr.status_text(True) == "Unsaved Changes"


def test_mark_saving():
    mgr = SaveStateManager()
    mgr.mark_saving()
    assert mgr.is_saving is True
    assert mgr.status_text(True) == "Saving..."
    assert mgr.status_text(False) == "Saving..."


def test_mark_saved():
    mgr = SaveStateManager()
    mgr.mark_saving()
    mgr.mark_saved()
    assert mgr.is_saving is False
    assert mgr.last_error is None
    assert mgr.status_text(False) == "Saved"


def test_mark_failed():
    mgr = SaveStateManager()
    mgr.mark_failed("Disk full")
    assert mgr.is_saving is False
    assert mgr.last_error == "Disk full"
    assert mgr.status_text(True) == "Save Failed"
    assert mgr.status_text(False) == "Save Failed"


def test_mark_failed_default_message():
    mgr = SaveStateManager()
    mgr.mark_failed()
    assert mgr.last_error == "Save failed"


def test_full_transition():
    mgr = SaveStateManager()
    assert mgr.status_text(True) == "Unsaved Changes"
    mgr.mark_saving()
    assert mgr.status_text(True) == "Saving..."
    mgr.mark_failed("Timeout")
    assert mgr.status_text(True) == "Save Failed"
    assert mgr.last_error == "Timeout"
    mgr.mark_saving()
    mgr.mark_saved()
    assert mgr.status_text(False) == "Saved"
