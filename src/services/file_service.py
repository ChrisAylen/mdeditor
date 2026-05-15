import os

class FileService:
    """
    Low-level wrapper for OS filesystem operations.
    """
    
    @staticmethod
    def read_file(path: str) -> str:
        """
        Reads the content of a file.
        Raises FileNotFoundError if the file does not exist.
        """
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def write_file(path: str, content: str) -> bool:
        """
        Writes content to a file.
        Returns True if successful, False otherwise.
        """
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception:
            return False
