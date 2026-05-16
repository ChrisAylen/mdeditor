from __future__ import annotations
from dataclasses import dataclass, field
from src.services.markdown_parser_service import OutlineNode


@dataclass
class OutlineState:
    tree: list[OutlineNode] = field(default_factory=list)
    active_heading_id: str | None = None
    selected_heading_id: str | None = None

    def update_tree(self, tree: list[OutlineNode]):
        self.tree = tree
        self.active_heading_id = None

    def set_active_by_line(self, line_number: int):
        best = self._find_closest_heading(self.tree, line_number)
        self.active_heading_id = best.id if best else None

    def select(self, heading_id: str | None):
        self.selected_heading_id = heading_id

    @staticmethod
    def _find_closest_heading(
        nodes: list[OutlineNode], line_number: int
    ) -> OutlineNode | None:
        best: OutlineNode | None = None
        for node in nodes:
            if node.line_number <= line_number:
                best = node
            child_best = OutlineState._find_closest_heading(
                node.children, line_number
            )
            if child_best:
                best = child_best
        return best
