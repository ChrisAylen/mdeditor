# mdeditor

A simple Markdown editor with AI integration, built with Python and PySide6.

## Download

### Linux
| Format | How to install |
|---|---|
| **AppImage** | Download `mdeditor-*.AppImage`, `chmod +x`, and run |
| **Ubuntu/Debian** | `sudo dpkg -i mdeditor_*.deb` |
| **pip** | `pip install mdeditor` |

### macOS
| Format | How to install |
|---|---|
| **DMG** | Download `mdeditor-*.dmg`, drag to Applications |
| **pip** | `pip install mdeditor` |

### Windows
| Format | How to install |
|---|---|
| **ZIP** | Download `mdeditor-*-windows-x86_64.zip`, extract, run `mdeditor.exe` |
| **pip** | `pip install mdeditor` |

### From source (any platform)
```bash
pip install git+https://github.com/ChrisAylen/mdeditor.git
mdeditor
```

## Features
- **Split-panel design**: raw markdown editing on the left, live formatted preview on the right.
- **Markdown rendering**: headings, bold, italic, tables, numbered lists, bullet lists, and task lists all render correctly.
- **Document Outline**: Dockable sidebar showing a real-time hierarchical heading outline; drag-and-drop reordering.
- **AI Chat Sidebar**: Conversational AI assistant with context modes (selected text, full document, or none).
- **AI actions**: Polish text, convert to table via right-click or AI menu (`Ctrl+Shift+P`, `Ctrl+Shift+T`).
- **Auto-save + recovery**: Automatic recovery snapshots; crash-safe with restore/discard prompt on startup.
- **Formatting menu**: headings (`Ctrl+1/2/3`), bold (`Ctrl+B`), italic (`Ctrl+I`), lists, tables, horizontal rules.
- **Decoupled architecture**: Logic is pure Python, independent of the Qt UI layer.

## Architecture
Decoupled layered architecture: `FileService` (IO) → `EditorState` (State) → `AppController` (Orchestration) → `UI` (Presentation).

## Running from source

```bash
python3 -m venv venv
source venv/bin/activate
pip install .
mdeditor
```

## Running Tests

```bash
pip install ".[dev]"
pytest tests/
```

Integration tests with Qt widgets require `QT_QPA_PLATFORM=offscreen` in headless environments.

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
