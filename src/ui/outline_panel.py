from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem
from PySide6.QtCore import Signal, Qt
from src.services.markdown_parser_service import OutlineNode


class OutlinePanel(QWidget):
    heading_clicked = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._node_map: dict[str, QTreeWidgetItem] = {}
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.empty_label = QLabel("No headings found\n\nAdd markdown headings (# ## ###)\nto generate an outline.")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setWordWrap(True)
        self.empty_label.setStyleSheet("color: #888; padding: 16px;")
        layout.addWidget(self.empty_label)

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setIndentation(16)
        self.tree.setAnimated(True)
        self.tree.setFocusPolicy(Qt.StrongFocus)
        self.tree.itemClicked.connect(self._on_item_clicked)
        layout.addWidget(self.tree)

    def update_outline(self, headings: list[OutlineNode]):
        self._node_map.clear()
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
            item.setData(0, Qt.UserRole, node.id)
            item.setToolTip(0, node.title)
            font = item.font(0)
            font.setBold(node.level == 1)
            item.setFont(0, font)
            parent.addChild(item)
            self._node_map[node.id] = item
            self._populate_tree(item, node.children)

    def highlight_heading(self, heading_id: str | None):
        for item_id, item in self._node_map.items():
            if item_id == heading_id:
                item.setSelected(True)
                self.tree.scrollToItem(item)
            else:
                item.setSelected(False)

    def _on_item_clicked(self, item: QTreeWidgetItem, _column: int):
        heading_id = item.data(0, Qt.UserRole)
        self.heading_clicked.emit(heading_id)
