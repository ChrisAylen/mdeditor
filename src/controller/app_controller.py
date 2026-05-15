from src.services.file_service import FileService
from src.logic.editor_state import EditorState

class AppController:
    """
    The orchestrator. Mediates between UI events, EditorState, and FileService.
    """
    
    def __init__(self, state: EditorState, file_service: FileService):
        self.state = state
        self.file_service = file_service

    def open_file(self, path: str):
        """
        Opens a file: reads content via FileService and updates EditorState.
        """
        content = self.file_service.read_file(path)
        self.state.set_path(path)
        self.state.set_content(content)
        self.state.mark_clean()

    def save_current_file(self) -> bool:
        """
        Saves the current state to the current file path.
        """
        if self.state.path is None:
            return False
            
        success = self.file_service.write_file(self.state.path, self.state.content)
        if success:
            self.state.mark_clean()
        return success

    def save_file_as(self, path: str) -> bool:
        """
        Saves the current state to a new file path.
        """
        success = self.file_service.write_file(path, self.state.content)
        if success:
            self.state.set_path(path)
            self.state.mark_clean()
        return success

    def create_new_file(self):
        """
        Resets the state for a new file.
        """
        self.state.set_path(None)
        self.state.set_content("")
        self.state.mark_clean()
