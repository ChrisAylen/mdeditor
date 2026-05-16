from PySide6.QtWidgets import (
    QMainWindow, QTextEdit, QVBoxLayout, QWidget, QHBoxLayout,
    QSplitter, QMenu, QMessageBox
)
from PySide6.QtCore import Qt, QThread, QSettings
import markdown
from src.ui.menu_bar import MenuBar
from src.ui.ai_worker import AiWorker
from src.ui.ai_settings_dialog import AiSettingsDialog

class MainWindow(QMainWindow):
    """
    Main window of the Markdown Editor.
    """
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Simple Markdown Editor")
        self.resize(800, 600)
        
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        # Menu Bar
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)
        
        # Main Splitter
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Editor (Left)
        self.editor = QTextEdit()
        self.splitter.addWidget(self.editor)
        
        # Preview (Right)
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.splitter.addWidget(self.preview)
        
        self.setCentralWidget(self.splitter)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)

        # Context menu for AI actions on editor
        self.editor.setContextMenuPolicy(Qt.CustomContextMenu)
        self.editor.customContextMenuRequested.connect(self._editor_context_menu)

    def _connect_signals(self):
        # Connect menu actions to controller methods
        self.menu_bar.action_new.triggered.connect(self._on_new)
        self.menu_bar.action_open.triggered.connect(self._on_open)
        self.menu_bar.action_save.triggered.connect(self._on_save)
        self.menu_bar.action_save_as.triggered.connect(self._on_save_as)
        self.menu_bar.action_exit.triggered.connect(self.close)

        # Connect format menu actions
        self.menu_bar.action_heading1.triggered.connect(lambda: self._insert_format("# "))
        self.menu_bar.action_heading2.triggered.connect(lambda: self._insert_format("## "))
        self.menu_bar.action_heading3.triggered.connect(lambda: self._insert_format("### "))
        self.menu_bar.action_bold.triggered.connect(lambda: self._wrap_selection("**", "**"))
        self.menu_bar.action_italic.triggered.connect(lambda: self._wrap_selection("*", "*"))
        self.menu_bar.action_bullet_list.triggered.connect(lambda: self._insert_format("- "))
        self.menu_bar.action_numbered_list.triggered.connect(lambda: self._insert_format("1. "))
        self.menu_bar.action_task_list.triggered.connect(lambda: self._insert_format("- [ ] "))
        self.menu_bar.action_table.triggered.connect(self._insert_table)
        self.menu_bar.action_horizontal_rule.triggered.connect(lambda: self._insert_at_cursor("\n---\n"))

        # Connect AI menu actions
        self.menu_bar.action_ai_polish.triggered.connect(lambda: self._run_ai("polish"))
        self.menu_bar.action_ai_table.triggered.connect(lambda: self._run_ai("table"))
        self.menu_bar.action_ai_settings.triggered.connect(self._show_ai_settings)

        # Sync editor content changes to state
        self.editor.textChanged.connect(self._on_text_changed)

    def _insert_at_cursor(self, text: str):
        cursor = self.editor.textCursor()
        cursor.insertText(text)
        self.editor.setTextCursor(cursor)

    def _insert_format(self, prefix: str):
        cursor = self.editor.textCursor()
        block = cursor.block()
        line_start = block.position()
        cursor.movePosition(cursor.MoveOperation.StartOfBlock)
        cursor.insertText(prefix)
        self.editor.setTextCursor(cursor)

    def _wrap_selection(self, before: str, after: str):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            selected = cursor.selectedText()
            cursor.insertText(f"{before}{selected}{after}")
        else:
            cursor.insertText(f"{before}{after}")
            cursor.movePosition(cursor.MoveOperation.Left, cursor.MoveMode.MoveAnchor, len(after))
        self.editor.setTextCursor(cursor)

    def _insert_table(self):
        cursor = self.editor.textCursor()
        block = cursor.block()
        cursor.movePosition(cursor.MoveOperation.StartOfBlock)
        table = (
            "| Column 1 | Column 2 | Column 3 |\n"
            "|----------|----------|----------|\n"
            "| Cell     | Cell     | Cell     |\n"
            "| Cell     | Cell     | Cell     |\n"
        )
        cursor.insertText(table)
        self.editor.setTextCursor(cursor)

    def _on_text_changed(self):
        content = self.editor.toPlainText()
        self.controller.state.content = content
        
        # Fix Task Lists: Use Unicode checkboxes (QTextEdit's HTML engine does not support <input>)
        import re
        processed_content = re.sub(r'^- \[ \]', '☐ ', content, flags=re.MULTILINE)
        processed_content = re.sub(r'^- \[x\]', '☑ ', processed_content, flags=re.MULTILINE)
        
        # Update Preview with extensions for tables and list styles
        # We use 'tables' extension (part of 'extra') for table support
        html_content = markdown.markdown(processed_content, extensions=['extra', 'sane_lists'])
        
        # Qt's QTextEdit.setHtml() has limited CSS support. 
        # To make tables look like tables, we wrap them in a basic style block.
        styled_html = f"""
        <style>
            table {{ border-collapse: collapse; border: 1px solid black; width: 100%; }}
            th, td {{ border: 1px solid black; padding: 4px; text-align: left; }}
            th {{ background-color: #f2f2f2; font-weight: bold; }}
        </style>
        {html_content}
        """
        self.preview.setHtml(styled_html)

    def _editor_context_menu(self, pos):
        cursor = self.editor.textCursor()
        has_selection = cursor.hasSelection()
        menu = self.editor.createStandardContextMenu()
        menu.addSeparator()
        ai_menu = menu.addMenu("AI")
        action_polish = ai_menu.addAction("Polish Text")
        action_polish.setEnabled(has_selection)
        action_table = ai_menu.addAction("Convert to Table")
        action_table.setEnabled(has_selection)
        action_polish.triggered.connect(lambda: self._run_ai("polish"))
        action_table.triggered.connect(lambda: self._run_ai("table"))
        menu.exec(self.editor.mapToGlobal(pos))

    def _get_ai_settings(self):
        settings = QSettings("mdeditor", "mdeditor")
        host = settings.value("ai/host", "http://localhost:11434")
        model = settings.value("ai/model", "")
        return host, model

    def _run_ai(self, action: str):
        host, model = self._get_ai_settings()
        if not model:
            QMessageBox.warning(
                self, "AI Not Configured",
                "No AI model configured. Please set one in AI > Settings."
            )
            self._show_ai_settings()
            host, model = self._get_ai_settings()
            if not model:
                return

        cursor = self.editor.textCursor()
        if not cursor.hasSelection():
            QMessageBox.information(self, "No Selection", "Select text first.")
            return

        selected_text = cursor.selectedText()

        prompts = {
            "polish": f"Improve the following markdown text for clarity, grammar, and correctness. Return only the improved text, no explanations:\n\n{selected_text}",
            "table": f"Convert the following data into a well-formatted markdown table. Return only the table, no explanations:\n\n{selected_text}",
        }

        prompt = prompts.get(action)
        if not prompt:
            return

        status_message = "Polishing..." if action == "polish" else "Converting to table..."
        self.statusBar().showMessage(status_message)

        self._ai_thread = QThread()
        self._ai_worker = AiWorker(host, model, prompt)
        self._ai_worker.moveToThread(self._ai_thread)
        self._ai_thread.started.connect(self._ai_worker.run)
        self._ai_worker.finished.connect(self._on_ai_result)
        self._ai_worker.error.connect(self._on_ai_error)
        self._ai_worker.finished.connect(self._ai_thread.quit)
        self._ai_worker.finished.connect(self._ai_worker.deleteLater)
        self._ai_worker.error.connect(self._ai_thread.quit)
        self._ai_worker.error.connect(self._ai_worker.deleteLater)
        self._ai_thread.finished.connect(self._ai_thread.deleteLater)
        self._ai_thread.start()

    def _on_ai_result(self, result: str):
        self.statusBar().clearMessage()
        self._insert_at_cursor(result)

    def _on_ai_error(self, error_msg: str):
        self.statusBar().clearMessage()
        QMessageBox.critical(self, "AI Error", f"AI request failed:\n{error_msg}")

    def _show_ai_settings(self):
        dialog = AiSettingsDialog(self)
        dialog.exec()

    def _on_new(self):
        if self._confirm_save():
            self.controller.create_new_file()
            self.editor.setPlainText("")
            self.preview.setHtml("")
            self._update_window_title()
    
    def _on_open(self):
        if self._confirm_save():
            from PySide6.QtWidgets import QFileDialog
            import re
            path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Markdown Files (*.md);;All Files (*)")
            if path:
                self.controller.open_file(path)
                content = self.controller.state.content
                self.editor.setPlainText(content)
                
                processed_content = re.sub(r'^- \[ \]', '☐ ', content, flags=re.MULTILINE)
                processed_content = re.sub(r'^- \[x\]', '☑ ', processed_content, flags=re.MULTILINE)
                
                html_content = markdown.markdown(processed_content, extensions=['extra', 'sane_lists'])
                styled_html = f"""
                <style>
                    table {{ border-collapse: collapse; border: 1px solid black; width: 100%; }}
                    th, td {{ border: 1px solid black; padding: 4px; text-align: left; }}
                    th {{ background-color: #f2f2f2; font-weight: bold; }}
                </style>
                {html_content}
                """
                self.preview.setHtml(styled_html)
                self._update_window_title()


    def _on_save_logic(self) -> bool:
        if self.controller.state.path is None:
            # Must save as
            from PySide6.QtWidgets import QFileDialog
            path, _ = QFileDialog.getSaveFileName(self, "Save File As", "", "Markdown Files (*.md);;All Files (*)")
            if path:
                if not path.endswith(".md"):
                    path += ".md"
                if self.controller.save_file_as(path):
                    self._update_window_title()
                    return True
            return False
        else:
            # Save current
            if self.controller.save_current_file():
                self._update_window_title()
                return True
            return False

    def _on_save(self):
        return self._on_save_logic()

    def _on_save_as(self):
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(self, "Save File As", "", "Markdown Files (*.md);;All Files (*)")
        if path:
            if not path.endswith(".md"):
                path += ".md"
            if self.controller.save_file_as(path):
                self._update_window_title()


    def _update_window_title(self):
        path = self.controller.state.path
        dirty = " *" if self.controller.state.is_dirty() else ""
        title = f"{path if path else 'Untitled'}{dirty} - Simple Markdown Editor"
        self.setWindowTitle(title)

    def _confirm_save(self) -> bool:
        from PySide6.QtWidgets import QMessageBox
        if not self.controller.state.is_dirty():
            return True
        
        reply = QMessageBox.question(
            self, "Unsaved Changes", 
            "The document has been modified. Do you want to save your changes?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
        )
        
        if reply == QMessageBox.Save:
            return self._on_save_logic()
        elif reply == QMessageBox.Discard:
            return True
        elif reply == QMessageBox.Cancel:
            return False
        return False

    def closeEvent(self, event):
        if self._confirm_save():
            event.accept()
        else:
            event.ignore()


