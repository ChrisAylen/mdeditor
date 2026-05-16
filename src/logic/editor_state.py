import uuid


class EditorState:
    """
    The 'Source of Truth' for the editor.
    Manages the current file path, content, and modification status.
    """

    def __init__(self):
        self._path = None
        self._content = ""
        self._is_dirty = False
        self._doc_id: str | None = None

    @property
    def path(self) -> str | None:
        return self._path

    @path.setter
    def path(self, value: str | None):
        self._path = value

    @property
    def content(self) -> str:
        return self._content

    @content.setter
    def content(self, value: str):
        if value != self._content:
            self._content = value
            self.mark_dirty()

    def set_path(self, path: str | None):
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

    @property
    def doc_id(self) -> str:
        if self._doc_id is None:
            self._doc_id = uuid.uuid4().hex[:12]
        return self._doc_id

    def reset_doc_id(self):
        self._doc_id = uuid.uuid4().hex[:12]
