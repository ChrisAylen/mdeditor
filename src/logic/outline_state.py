from __future__ import annotations
from dataclasses import dataclass, field
from src.services.markdown_parser_service import OutlineNode


@dataclass
class OutlineState:
    tree: list[OutlineNode] = field(default_factory=list)
    active_heading_line: int | None = None
    selected_heading_line: int | None = None

    def update_tree(self, tree: list[OutlineNode]):
        self.tree = tree
        self.active_heading_line = None

    def set_active_by_line(self, line_number: int):
        best = self._find_closest_heading(self.tree, line_number)
        self.active_heading_line = best.line_number if best else None

    def select(self, heading_line: int | None):
        self.selected_heading_line = heading_line

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
