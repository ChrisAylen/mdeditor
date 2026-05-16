from PySide6.QtWidgets import QMenuBar
from PySide6.QtGui import QAction

class MenuBar(QMenuBar):
    """
    Defines the application menu bar.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_menus()

    def _setup_menus(self):
        # File Menu
        self.file_menu = self.addMenu("&File")
        
        self.action_new = self.file_menu.addAction("&New")
        self.action_open = self.file_menu.addAction("&Open")
        self.action_save = self.file_menu.addAction("&Save")
        self.action_save_as = self.file_menu.addAction("Save &As...")
        
        self.file_menu.addSeparator()
        self.action_exit = self.file_menu.addAction("&Exit")

        # Format Menu
        self.format_menu = self.addMenu("F&ormat")
        
        self.action_heading1 = self.format_menu.addAction("Heading &1")
        self.action_heading2 = self.format_menu.addAction("Heading &2")
        self.action_heading3 = self.format_menu.addAction("Heading &3")
        self.action_heading1.setShortcut("Ctrl+1")
        self.action_heading2.setShortcut("Ctrl+2")
        self.action_heading3.setShortcut("Ctrl+3")
        
        self.format_menu.addSeparator()
        
        self.action_bold = self.format_menu.addAction("&Bold")
        self.action_bold.setShortcut("Ctrl+B")
        self.action_italic = self.format_menu.addAction("&Italic")
        self.action_italic.setShortcut("Ctrl+I")
        
        self.format_menu.addSeparator()
        
        self.action_bullet_list = self.format_menu.addAction("&Bullet List")
        self.action_numbered_list = self.format_menu.addAction("&Numbered List")
        self.action_task_list = self.format_menu.addAction("&Task List")
        
        self.format_menu.addSeparator()
        
        self.action_table = self.format_menu.addAction("&Table")
        self.action_horizontal_rule = self.format_menu.addAction("Horizontal &Rule")

        # AI Menu
        self.ai_menu = self.addMenu("&AI")

        self.action_ai_polish = self.ai_menu.addAction("&Polish Text")
        self.action_ai_polish.setShortcut("Ctrl+Shift+P")
        self.action_ai_table = self.ai_menu.addAction("Convert to &Table")
        self.action_ai_table.setShortcut("Ctrl+Shift+T")

        self.ai_menu.addSeparator()

        self.action_ai_settings = self.ai_menu.addAction("&Settings...")
