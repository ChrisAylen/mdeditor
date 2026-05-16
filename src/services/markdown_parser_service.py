from __future__ import annotations
from dataclasses import dataclass, field
import re
import uuid


@dataclass
class OutlineNode:
    id: str
    level: int
    title: str
    line_number: int
    children: list[OutlineNode] = field(default_factory=list)


class MarkdownParserService:
    FENCE_PATTERN = re.compile(r"^(```|~~~)")

    @staticmethod
    def parse_headings(markdown_text: str) -> list[OutlineNode]:
        lines = markdown_text.split("\n")
        flat_headings = MarkdownParserService._extract_headings(lines)
        return MarkdownParserService._build_tree(flat_headings)

    @staticmethod
    def extract_headings_flat(markdown_text: str) -> list[OutlineNode]:
        lines = markdown_text.split("\n")
        return MarkdownParserService._extract_headings(lines)

    @staticmethod
    def _extract_headings(lines: list[str]) -> list[OutlineNode]:
        headings: list[OutlineNode] = []
        in_fence = False

        for lineno, line in enumerate(lines, start=1):
            stripped = line.strip()

            if MarkdownParserService.FENCE_PATTERN.match(stripped):
                in_fence = not in_fence
                continue

            if in_fence:
                continue

            if not stripped.startswith("#"):
                continue

            level = 0
            for ch in stripped:
                if ch == "#":
                    level += 1
                else:
                    break

            if level < 1 or level > 6:
                continue

            if len(stripped) <= level or stripped[level] != " ":
                continue

            title = stripped[level:].strip()
            if not title:
                continue

            headings.append(
                OutlineNode(
                    id=str(uuid.uuid4()),
                    level=level,
                    title=title,
                    line_number=lineno,
                )
            )

        return headings

    @staticmethod
    def build_tree(headings: list[OutlineNode]) -> list[OutlineNode]:
        return MarkdownParserService._build_tree(headings)

    @staticmethod
    def _build_tree(headings: list[OutlineNode]) -> list[OutlineNode]:
        root: list[OutlineNode] = []
        stack: list[OutlineNode] = []

        for heading in headings:
            while stack and stack[-1].level >= heading.level:
                stack.pop()

            if stack:
                stack[-1].children.append(heading)
            else:
                root.append(heading)

            stack.append(heading)

        return root

    @staticmethod
    def move_section(
        markdown_text: str,
        flat_headings: list[OutlineNode],
        source_id: str,
        target_id: str,
        position: str,
    ) -> str:
        source = _find_by_id(flat_headings, source_id)
        target = _find_by_id(flat_headings, target_id)
        if source is None or target is None or source_id == target_id:
            return markdown_text

        source_idx = next(i for i, h in enumerate(flat_headings) if h.id == source_id)
        target_idx = next(i for i, h in enumerate(flat_headings) if h.id == target_id)

        lines = markdown_text.split("\n")

        src_start = source.line_number - 1
        src_end = _section_end(flat_headings, source_idx, len(lines))

        tgt_start = target.line_number - 1

        source_lines = lines[src_start:src_end]

        if position == "child":
            new_level = min(source.level + 1, 6)
            old_prefix = "#" * source.level
            new_prefix = "#" * new_level
            source_lines[0] = source_lines[0].replace(old_prefix, new_prefix, 1)

        remaining = lines[:src_start] + lines[src_end:]

        removed_count = src_end - src_start
        if target.line_number > source.line_number:
            tgt_line_adj = tgt_start - removed_count
        else:
            tgt_line_adj = tgt_start

        if position == "before":
            insert_at = tgt_line_adj
        elif position == "after":
            tgt_end = _section_end(flat_headings, target_idx, len(lines)) - removed_count
            insert_at = tgt_end
        else:
            insert_at = tgt_line_adj + 1

        result_lines = remaining[:insert_at] + source_lines + remaining[insert_at:]
        return "\n".join(result_lines)


def _find_by_id(nodes: list[OutlineNode], heading_id: str) -> OutlineNode | None:
    for node in nodes:
        if node.id == heading_id:
            return node
    return None


def _section_end(flat: list[OutlineNode], idx: int, total_lines: int) -> int:
    current = flat[idx]
    for i in range(idx + 1, len(flat)):
        if flat[i].level <= current.level:
            return flat[i].line_number - 1
    return total_lines
