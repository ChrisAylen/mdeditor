class EditorState:
    """
    The 'Source of Truth' for the editor. 
    Manages the current file path, content, and modification status.
    """
    
    def __init__(self):
        self._path = None
        self._content = ""
        self._is_dirty = False

    @property
    def path(self) -> str:
        return self._path

    @path.setter
    def path(self, value: str):
        self._path = value

    @property
    def content(self) -> str:
        return self._content

    @content.setter
    def content(self, value: str):
        if value != self._content:
            self._content = value
            self.mark_dirty()

    def set_path(self, path: str):
        self._path = path

    def set_content(self, text: str):
        if text != self._content:
            self._content = text
            self.mark_dirty()

    def mark_dirty(self):
        self._is_dirty = True

    def mark_clean(self):
        self._is_dirty = False

    def is_dirty(self) -> bool:
        return self._is_dirty
