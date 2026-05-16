import pytest
from src.services.recovery_service import RecoveryService


def test_no_recoveries_initially(tmp_path, monkeypatch):
    monkeypatch.setattr(RecoveryService, "_get_recovery_dir", lambda: str(tmp_path))
    assert RecoveryService.has_recoveries() is False
    assert RecoveryService.list_recoveries() == []


def test_save_and_load_recovery(tmp_path, monkeypatch):
    monkeypatch.setattr(RecoveryService, "_get_recovery_dir", lambda: str(tmp_path))
    result = RecoveryService.save_recovery("Hello World", "/path/to/file.md", "doc1")
    assert result is True

    content = RecoveryService.load_recovery("doc1")
    assert content == "Hello World"

    meta = RecoveryService.load_metadata("doc1")
    assert meta is not None
    assert meta["doc_id"] == "doc1"
    assert meta["original_path"] == "/path/to/file.md"
    assert "timestamp" in meta


def test_load_recovery_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(RecoveryService, "_get_recovery_dir", lambda: str(tmp_path))
    content = RecoveryService.load_recovery("nonexistent")
    assert content is None


def test_load_metadata_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(RecoveryService, "_get_recovery_dir", lambda: str(tmp_path))
    meta = RecoveryService.load_metadata("nonexistent")
    assert meta is None


def test_has_recoveries_after_save(tmp_path, monkeypatch):
    monkeypatch.setattr(RecoveryService, "_get_recovery_dir", lambda: str(tmp_path))
    RecoveryService.save_recovery("content", None, "doc1")
    assert RecoveryService.has_recoveries() is True


def test_list_recoveries(tmp_path, monkeypatch):
    monkeypatch.setattr(RecoveryService, "_get_recovery_dir", lambda: str(tmp_path))
    RecoveryService.save_recovery("content1", "/path/1.md", "doc1")
    RecoveryService.save_recovery("content2", None, "doc2")

    recoveries = RecoveryService.list_recoveries()
    assert len(recoveries) == 2
    doc_ids = {r["doc_id"] for r in recoveries}
    assert doc_ids == {"doc1", "doc2"}


def test_clear_recovery(tmp_path, monkeypatch):
    monkeypatch.setattr(RecoveryService, "_get_recovery_dir", lambda: str(tmp_path))
    RecoveryService.save_recovery("content", None, "doc1")
    assert RecoveryService.has_recoveries() is True

    RecoveryService.clear_recovery("doc1")
    assert RecoveryService.has_recoveries() is False


def test_clear_all_recoveries(tmp_path, monkeypatch):
    monkeypatch.setattr(RecoveryService, "_get_recovery_dir", lambda: str(tmp_path))
    RecoveryService.save_recovery("content1", None, "doc1")
    RecoveryService.save_recovery("content2", None, "doc2")
    assert RecoveryService.has_recoveries() is True

    RecoveryService.clear_all_recoveries()
    assert RecoveryService.has_recoveries() is False


def test_save_recovery_failure(monkeypatch):
    def mock_makedirs(*args, **kwargs):
        raise OSError("Permission denied")
    monkeypatch.setattr("os.makedirs", mock_makedirs)
    result = RecoveryService.save_recovery("content", None, "doc1")
    assert result is False


def test_load_recovery_returns_none_on_error(monkeypatch):
    monkeypatch.setattr("builtins.open", lambda *a, **kw: (_ for _ in ()).throw(OSError("Bad")))
    result = RecoveryService.load_recovery("doc1")
    assert result is None
