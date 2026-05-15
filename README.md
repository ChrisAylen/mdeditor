# Markdown Editor

A simple Markdown editor built with Python and PySide6, following a decoupled layered architecture.

## Features
- Open, edit, and save Markdown files.
- Split-panel design: raw markdown editing on the left, live formatted preview on the right.
- Automatic `.md` extension for new files.
- Decoupled architecture for easy maintenance and testing.

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
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
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
pip install -r requirements-dev.txt
PYTHONPATH=. pytest tests/
```
