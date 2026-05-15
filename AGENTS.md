# AGENTS.md

## Architecture & Design
- **Pattern**: Decoupled Layered Architecture. Logic must be entirely independent of the UI.
- **Flow**: `FileService` (IO) $\rightarrow$ `EditorState` (State) $\rightarrow$ `AppController` (Orchestration) $\rightarrow$ `UI` (Presentation).
- **Framework**: PySide6 (Qt 6).

## Project Structure
- `src/services/`: File I/O (`file_service.py`)
- `src/logic/`: State tracking (`editor_state.py`)
- `src/controller/`: Orchestration (`app_controller.py`)
- `src/ui/`: Windows and menus (`main_window.py`, `menu_bar.py`)
- `src/main.py`: Application entry point
- `tests/unit/` & `tests/integration/`: Test suites

## Implementation Roadmap & Quality Gates
Follow this strict sequence. Do not proceed to the next phase until the quality gate is passed:
1. **FileService**: 100% pass on read/write unit tests.
2. **EditorState**: All state transition tests pass (Dirty $\leftrightarrow$ Clean).
3. **AppController**: Mocked I/O tests pass; state managed correctly.
4. **UI Layout**: Application launches on Ubuntu; components visible.
5. **Integration**: End-to-end flow: Create $\rightarrow$ Edit $\rightarrow$ Save $\rightarrow$ Re-open.

## Development Commands
- **Dev Dependencies**: `pip install -r requirements-dev.txt`
- **Run Tests**: `pytest tests/`
- **Run App**: `python3 src/main.py`

## Testing Conventions
- **File Ops**: Use `pytest` `tmp_path` fixture to prevent system residue.
- **UI Tests**: Use `pytest-qt` to simulate interactions and verify Controller method invocation.
