from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem, QAbstractItemView
from PySide6.QtCore import Signal, Qt
from src.services.markdown_parser_service import OutlineNode


class _DragDropTree(QTreeWidget):
    item_dropped = Signal(int, int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._drag_source_line: int | None = None

    def startDrag(self, supported_actions):
        item = self.currentItem()
        if item:
            self._drag_source_line = item.data(0, Qt.UserRole)
        super().startDrag(supported_actions)

    def dropEvent(self, event):
        source_line = self._drag_source_line
        target_item = self.itemAt(event.position().toPoint())
        if not target_item or source_line is None:
            event.ignore()
            return

        target_line = target_item.data(0, Qt.UserRole)
        if source_line == target_line:
            event.ignore()
            return

        rect = self.visualItemRect(target_item)
        y_in_item = event.position().toPoint().y() - rect.y()
        ratio = y_in_item / rect.height() if rect.height() > 0 else 0.5

        if ratio < 0.3:
            position = "before"
        elif ratio > 0.7:
            position = "after"
        else:
            position = "child"

        event.setDropAction(Qt.MoveAction)
        super().dropEvent(event)
        self._drag_source_line = None
        self.item_dropped.emit(source_line, target_line, position)


class OutlinePanel(QWidget):
    heading_clicked = Signal(int)
    heading_moved = Signal(int, int, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._line_map: dict[int, QTreeWidgetItem] = {}
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.empty_label = QLabel("No headings found\n\nAdd markdown headings (# ## ###)\nto generate an outline.")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setWordWrap(True)
        self.empty_label.setStyleSheet("color: #888; padding: 16px;")
        layout.addWidget(self.empty_label)

        self.tree = _DragDropTree()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(16)
        self.tree.setAnimated(True)
        self.tree.setFocusPolicy(Qt.StrongFocus)
        self.tree.setDragEnabled(True)
        self.tree.setAcceptDrops(True)
        self.tree.setDropIndicatorShown(True)
        self.tree.setDragDropMode(QAbstractItemView.InternalMove)
        self.tree.itemClicked.connect(self._on_item_clicked)
        self.tree.item_dropped.connect(self._on_item_dropped)
        layout.addWidget(self.tree)

    def update_outline(self, headings: list[OutlineNode]):
        self._line_map.clear()
        self.tree.clear()

        if not headings:
            self.empty_label.show()
            self.tree.hide()
            return

        self.empty_label.hide()
        self.tree.show()
        self._populate_tree(self.tree.invisibleRootItem(), headings)

    def _populate_tree(self, parent: QTreeWidgetItem, nodes: list[OutlineNode]):
        for node in nodes:
            item = QTreeWidgetItem()
            item.setText(0, node.title)
            item.setData(0, Qt.UserRole, node.line_number)
            item.setToolTip(0, node.title)
            font = item.font(0)
            font.setBold(node.level == 1)
            item.setFont(0, font)
            parent.addChild(item)
            self._line_map[node.line_number] = item
            self._populate_tree(item, node.children)

    def highlight_heading(self, heading_line: int | None):
        for line, item in self._line_map.items():
            if line == heading_line:
                item.setSelected(True)
                self.tree.scrollToItem(item)
            else:
                item.setSelected(False)

    def _on_item_clicked(self, item: QTreeWidgetItem, _column: int):
        line = item.data(0, Qt.UserRole)
        self.heading_clicked.emit(line)

    def _on_item_dropped(self, source_line: int, target_line: int, position: str):
        self.heading_moved.emit(source_line, target_line, position)
