# Development Plan: Simple Markdown Editor (Ubuntu)

**Role:** Senior Software Architect & Delivery Lead  
**Project:** Ubuntu Markdown Editor (MVP)  
**Status:** Planning Phase

---

## 1. Architecture

The application will follow a **Decoupled Layered Architecture**, ensuring that the business logic (file handling and state) is entirely independent of the presentation layer (GUI). This allows for rigorous TDD and ensures that the UI can be swapped or modified without breaking core functionality.

### Proposed Module Structure
- **`FileService`**: Low-level wrapper for OS filesystem operations.
- **`EditorState`**: The "Source of Truth". Manages the current file path, current text content, and the "dirty" flag (unsaved changes).
- **`AppController`**: The orchestrator. It mediates between the UI events and the logic modules.
- **`UI Components`**: The PySide6 implementation of the windows, menus, and text areas.

### Module Responsibilities & Interactions
| Module | Responsibility | Interaction |
| :--- | :--- | :--- |
| **FileService** | Reading/writing `.md` files to disk. | Called by `AppController`. |
| **EditorState** | Tracking the current open file and modification status. | Updated by `AppController`; read by `UI`. |
| **AppController** | Executing application logic (e.g., "Save As" workflow). | Bridges `UI` $\leftrightarrow$ `EditorState` $\leftrightarrow$ `FileService`. |
| **UI Layer** | Rendering the window, handling clicks/keystrokes. | Sends events to `AppController`. |

### Separation Concerns
- **UI**: No logic regarding how a file is saved; it only knows that a "Save" button was clicked.
- **File Handling**: No knowledge of the GUI; it only deals with strings and paths.
- **Editor State**: A pure Python object tracking the current session state.

---

## 2. Recommended Implementation: PySide6

**Recommendation:** **PySide6** (The official Python bindings for Qt 6).

**Justification:**
1. **Native Look & Feel:** PySide6 integrates seamlessly with Ubuntu's window managers, providing a professional desktop experience.
2. **Licensing:** PySide6 is licensed under LGPL, which is more permissive for various project types than PyQt6's GPL.
3. **Robust Widget Set:** The `QTextEdit` and `QMainWindow` components provide a stable foundation for a text editor without needing to build basic UI elements from scratch.
4. **Maintainability:** Qt's signal-and-slot mechanism is ideal for the modular, event-driven architecture required here.

---

## 3. Development Phases

### Phase 1: File Service (The Foundation)
*   **Purpose:** Secure, reliable reading and writing of files to the Ubuntu filesystem.
*   **Files:** `src/services/file_service.py`
*   **Public API:** 
    *   `read_file(path: str) -> str`
    *   `write_file(path: str, content: str) -> bool`
*   **Acceptance Criteria:** Ability to read a `.md` file and write a string to a file without encoding errors.
*   **Tests:**
    *   Test reading a non-existent file (should raise `FileNotFoundError`).
    *   Test writing a string to a temporary file and verifying contents.
    *   Test reading a file with UTF-8 characters.
*   **Manual Verification:** Run a script that creates a file and reads it back.

### Phase 2: Editor State Management
*   **Purpose:** Manage the lifecycle of the currently active document.
*   **Files:** `src/logic/editor_state.py`
*   **Public API:** 
    *   `set_content(text: str)`
    *   `set_path(path: str)`
    *   `mark_dirty()` / `mark_clean()`
    *   `is_dirty() -> bool`
*   **Acceptance Criteria:** The state correctly reflects whether the current content differs from the saved version on disk.
*   **Tests:**
    *   Verify `is_dirty` is false on initial load.
    *   Verify `is_dirty` becomes true after `set_content` is called.
    *   Verify `is_dirty` becomes false after a simulated save.
*   **Manual Verification:** Unit test suite execution.

### Phase 3: Application Controller
*   **Purpose:** Coordinate the "Business Logic" (e.g., the sequence of events for "Save As").
*   **Files:** `src/controller/app_controller.py`
*   **Public API:** 
    *   `open_file(path: str)`
    *   `save_current_file()`
    *   `save_file_as(path: str)`
    *   `create_new_file()`
*   **Acceptance Criteria:** The controller successfully updates the `EditorState` and calls the `FileService` in the correct order.
*   **Tests:**
    *   Mock `FileService` to ensure `write_file` is called during `save_current_file`.
    *   Verify `open_file` updates the `EditorState` with the correct path.
*   **Manual Verification:** Unit test suite execution.

### Phase 4: Basic UI Layout
*   **Purpose:** Implement the visual shell and text entry area.
*   **Files:** `src/ui/main_window.py`, `src/ui/menu_bar.py`
*   **Public API:** 
    *   `MainWindow` class (inheriting from `QMainWindow`).
*   **Acceptance Criteria:** Application opens a window with a text area and a menu bar (File $\rightarrow$ New, Open, Save, Save As).
*   **Tests:**
    *   Smoke test: Ensure the window initialises without crashing.
    *   Verify UI elements (TextEdit, MenuItems) exist in the object tree.
*   **Manual Verification:** Launch app; verify window appears and menus are clickable.

### Phase 5: UI-Logic Integration
*   **Purpose:** Connect UI signals to Controller methods.
*   **Files:** `src/main.py` (Entry point), `src/ui/main_window.py`
*   **Public API:** Wiring signals (e.g., `actionSave.triggered.connect(controller.save_current_file)`).
*   **Acceptance Criteria:** User can create, open, edit, and save a file through the GUI.
*   **Tests:**
    *   Integration test: Trigger "Open" dialogue $\rightarrow$ verify text appears in editor.
    *   Integration test: Edit text $\rightarrow$ trigger "Save" $\rightarrow$ verify file exists on disk.
*   **Manual Verification:** End-to-end walkthrough of the required features.

---

## 4. Testing Strategy

### Unit Tests
- **Framework:** `pytest`
- **File Ops:** Use `pytest`'s `tmp_path` fixture to create temporary directories and files for every test, ensuring no residue is left on the Ubuntu system.
- **State/Logic:** Pure Python tests with no GUI dependency.
- **Unsaved Changes:** Specifically test the logic that triggers a "Save changes?" prompt by simulating a state change and then attempting to close the file.

### UI Smoke Tests
- Use `pytest-qt` to simulate button clicks and verify that the correct Controller methods are invoked.

### Execution on Ubuntu
Tests will be executed via the terminal:
```bash
pip install -r requirements-dev.txt
pytest tests/
```

---

## 5. Suggested Project Structure

```text
/md-editor
  /src
    /__init__.py
    /services
      /__init__.py
      /file_service.py      # File I/O logic
    /logic
      /__init__.py
      /editor_state.py      # Current state tracking
    /controller
      /__init__.py
      /app_controller.py    # Coordination logic
    /ui
      /__init__.py
      /main_window.py       # Main UI Frame
      /menu_bar.py          # Menu definitions
    /main.py                # Application entry point
  /tests
    /unit
      /test_file_service.py
      /test_editor_state.py
      /test_app_controller.py
    /integration
      /test_ui_flow.py
  README.md
  requirements.txt          # Production dependencies (PySide6)
  requirements-dev.txt      # Development dependencies (pytest, pytest-qt)
  pyproject.toml            # Build system configuration
```

---

## 6. Incremental Build Order & Quality Gates

| Order | Module | Quality Gate (Must pass to proceed) |
| :--- | :--- | :--- |
| 1 | `FileService` | 100% pass rate on file read/write unit tests. |
| 2 | `EditorState` | All state transition tests pass (Dirty $\leftrightarrow$ Clean). |
| 3 | `AppController` | Mocked I/O tests pass; Controller correctly manages State. |
| 4 | `UI Layout` | Application launches on Ubuntu; UI components visible. |
| 5 | `Integration` | End-to-end test: Create $\rightarrow$ Edit $\rightarrow$ Save $\rightarrow$ Re-open. |

---

## 7. README Requirements

The final README must contain the following sections:
1. **Installation:** Instructions for installing Python 3 and running `pip install -r requirements.txt`.
2. **Execution:** Command to start the app (`python3 src/main.py`).
3. **Testing:** Instructions for running the pytest suite.
4. **User Guide:**
    - How to create a new file.
    - How to open existing `.md` files.
    - How to save and "Save As".
5. **Known Limitations:** (e.g., "No live preview in MVP", "Basic text editing only").
6. **Future Enhancements:** List of planned features.

---

## 8. Future Enhancements

These features are explicitly excluded from the MVP but are planned for Version 2.0:
- **Live Preview:** A split-screen view using a Markdown rendering library (e.g., `markdown-it-py`) and `QTextBrowser`.
- **Dark Mode:** CSS-based styling for the `QTextEdit` widget.
- **Word Count:** A status bar indicator updating in real-time.
- **Recent Files:** A history list stored in a local `.conf` file.
- **Find/Replace:** A modal dialogue for text manipulation.
- **Packaging:** Creating a `.deb` package or an AppImage for easier Ubuntu distribution.
