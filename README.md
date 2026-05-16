# Markdown Editor

A simple Markdown editor built with Python and PySide6, following a decoupled layered architecture.

## Features
- **Split-panel design**: raw markdown editing on the left, live formatted preview on the right.
- **Markdown rendering**: headings, bold, italic, tables, numbered lists, bullet lists, and task lists all render correctly.
- **Formatting menu**: Insert headings, lists, tables, bold/italic, and horizontal rules via the Format menu or keyboard shortcuts.
- **File operations**: Open, edit, save, and save-as Markdown files. New files automatically get a `.md` extension.
- **AI integration** (via Ollama):
  - Select text, right-click, and choose **Polish Text** or **Convert to Table**.
  - Same actions available under the **AI** menu with keyboard shortcuts (`Ctrl+Shift+P`, `Ctrl+Shift+T`).
  - Configurable Ollama host and model selection via **AI → Settings**.
  - Supports any Ollama model plus custom/frontier model endpoints.
  - All AI calls run asynchronously — the UI stays responsive.
- **Decoupled architecture** for easy maintenance and testing.

## Architecture
The project uses a Layered Architecture to ensure logic is independent of the UI:
- **FileService**: Handles file I/O operations.
- **EditorState**: Manages the state of the editor (e.g., whether the document is dirty).
- **AppController**: Orchestrates the flow between the state, service, and UI.
- **UI**: Presentation layer built with PySide6.

## Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation
1. Clone the repository.
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application
```bash
python3 -m src.main
```

### Running Tests
```bash
pip install pytest
PYTHONPATH=. pytest tests/
```

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+N` | New file |
| `Ctrl+O` | Open file |
| `Ctrl+S` | Save |
| `Ctrl+Shift+S` | Save As |
| `Ctrl+1/2/3` | Heading 1/2/3 |
| `Ctrl+B` | Bold |
| `Ctrl+I` | Italic |
| `Ctrl+Shift+P` | AI Polish Text |
| `Ctrl+Shift+T` | AI Convert to Table |

## AI Configuration

1. Ensure [Ollama](https://ollama.ai) is running locally (default: `http://localhost:11434`).
2. Pull a model: `ollama pull llama3.2` (or any model of your choice).
3. In the editor, go to **AI → Settings**, select your model, and save.
4. Select text in the editor, right-click, and choose **Polish Text** or **Convert to Table**.

You can also enter custom/frontier model endpoints manually in the Model field.
