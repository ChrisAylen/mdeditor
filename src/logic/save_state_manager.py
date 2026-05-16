class SaveStateManager:
    SAVED = "saved"
    UNSAVED = "unsaved"
    SAVING = "saving"
    SAVE_FAILED = "save_failed"

    def __init__(self):
        self._is_saving = False
        self._last_error: str | None = None

    @property
    def is_saving(self) -> bool:
        return self._is_saving

    def mark_saving(self):
        self._is_saving = True

    def mark_saved(self):
        self._is_saving = False
        self._last_error = None

    def mark_failed(self, error: str | None = None):
        self._is_saving = False
        self._last_error = error or "Save failed"

    @property
    def last_error(self) -> str | None:
        return self._last_error

    def status_text(self, is_dirty: bool) -> str:
        if self._is_saving:
            return "Saving..."
        if self._last_error:
            return "Save Failed"
        if is_dirty:
            return "Unsaved Changes"
        return "Saved"
