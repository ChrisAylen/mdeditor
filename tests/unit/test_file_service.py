import pytest
from src.services.file_service import FileService

def test_read_file_success(tmp_path):
    # Create a temporary file
    path = tmp_path / "test.md"
    content = "Hello Markdown"
    path.write_text(content, encoding="utf-8")
    
    # Test reading the file
    assert FileService.read_file(str(path)) == content

def test_read_file_not_found():
    # Test reading a non-existent file
    with pytest.raises(FileNotFoundError):
        FileService.read_file("non_existent_file.md")

def test_read_file_utf8(tmp_path):
    # Test reading a file with UTF-8 characters
    path = tmp_path / "utf8.md"
    content = "Hello 🌍 Markdown"
    path.write_text(content, encoding="utf-8")
    
    assert FileService.read_file(str(path)) == content

def test_write_file_success(tmp_path):
    # Test writing a string to a temporary file
    path = tmp_path / "write_test.md"
    content = "Written content"
    
    result = FileService.write_file(str(path), content)
    
    assert result is True
    assert path.read_text(encoding="utf-8") == content

def test_write_file_failure(monkeypatch):
    # Simulate a write failure by patching open
    def mock_open(*args, **kwargs):
        raise IOError("Disk full")
    
    monkeypatch.setattr("builtins.open", mock_open)
    
    result = FileService.write_file("dummy_path.md", "some content")
    assert result is False
