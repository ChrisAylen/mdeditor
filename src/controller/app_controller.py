from src.services.file_service import FileService
from src.services.recovery_service import RecoveryService
from src.logic.editor_state import EditorState
from src.logic.save_state_manager import SaveStateManager


class AppController:
    """
    The orchestrator. Mediates between UI events, EditorState, FileService, and
    recovery/auto-save infrastructure.
    """

    def __init__(
        self,
        state: EditorState,
        file_service: FileService,
        recovery_service: RecoveryService | None = None,
        save_state_manager: SaveStateManager | None = None,
    ):
        self.state = state
        self.file_service = file_service
        self.recovery_service = recovery_service or RecoveryService()
        self.save_state_manager = save_state_manager or SaveStateManager()

    def open_file(self, path: str):
        content = self.file_service.read_file(path)
        self.state.set_path(path)
        self.state.set_content(content)
        self.state.mark_clean()
        self.state.reset_doc_id()

    def save_current_file(self) -> bool:
        if self.state.path is None:
            return False
        self.save_state_manager.mark_saving()
        success = self.file_service.write_file(self.state.path, self.state.content)
        if success:
            self.state.mark_clean()
            self.save_state_manager.mark_saved()
            self.recovery_service.clear_recovery(self.state.doc_id)
        else:
            self.save_state_manager.mark_failed()
        return success

    def save_file_as(self, path: str) -> bool:
        self.save_state_manager.mark_saving()
        success = self.file_service.write_file(path, self.state.content)
        if success:
            self.state.set_path(path)
            self.state.mark_clean()
            self.save_state_manager.mark_saved()
            self.recovery_service.clear_recovery(self.state.doc_id)
        else:
            self.save_state_manager.mark_failed()
        return success

    def create_new_file(self):
        self.state.set_path(None)
        self.state.set_content("")
        self.state.mark_clean()
        self.state.reset_doc_id()

    def save_recovery(self) -> bool:
        return self.recovery_service.save_recovery(
            content=self.state.content,
            original_path=self.state.path,
            doc_id=self.state.doc_id,
        )

    def has_recovery(self) -> bool:
        return self.recovery_service.has_recoveries()

    def list_recoveries(self) -> list[dict]:
        return self.recovery_service.list_recoveries()

    def recover_content(self, doc_id: str) -> str | None:
        return self.recovery_service.load_recovery(doc_id)

    def discard_recovery(self, doc_id: str):
        self.recovery_service.clear_recovery(doc_id)
