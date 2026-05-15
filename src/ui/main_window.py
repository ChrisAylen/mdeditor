from PySide6.QtWidgets import QMainWindow, QTextEdit, QVBoxLayout, QWidget, QHBoxLayout, QSplitter
from PySide6.QtCore import Qt
import markdown
from src.ui.menu_bar import MenuBar

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


