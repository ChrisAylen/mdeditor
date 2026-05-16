from __future__ import annotations
from dataclasses import dataclass, field
import re


@dataclass
class OutlineNode:
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
        source_line: int,
        target_line: int,
        position: str,
    ) -> str:
        flat = MarkdownParserService.extract_headings_flat(markdown_text)

        source_idx = None
        target_idx = None
        for i, h in enumerate(flat):
            if h.line_number == source_line:
                source_idx = i
            if h.line_number == target_line:
                target_idx = i

        if source_idx is None or target_idx is None or source_idx == target_idx:
            return markdown_text

        source = flat[source_idx]
        target = flat[target_idx]

        lines = markdown_text.split("\n")

        src_start = source.line_number - 1
        src_end = _section_end(flat, source_idx, len(lines))

        # Prevent moving source onto/into its own section
        if source.line_number < target.line_number <= src_end:
            return markdown_text

        # Collect all headings within the moved section
        section_headings = [source]
        for i in range(source_idx + 1, len(flat)):
            if flat[i].line_number - 1 >= src_end:
                break
            section_headings.append(flat[i])

        # Determine new level for the top heading based on target context
        if position == "child":
            new_top_level = min(target.level + 1, 6)
        else:
            new_top_level = target.level

        delta = new_top_level - source.level

        source_lines = lines[src_start:src_end]

        if delta != 0:
            for h in section_headings:
                idx = h.line_number - 1 - src_start
                old_prefix = "#" * h.level
                new_level = max(1, min(h.level + delta, 6))
                new_prefix = "#" * new_level
                source_lines[idx] = source_lines[idx].replace(old_prefix, new_prefix, 1)

        remaining = lines[:src_start] + lines[src_end:]

        removed_count = src_end - src_start
        if target.line_number > source.line_number:
            tgt_line_adj = (target.line_number - 1) - removed_count
        else:
            tgt_line_adj = target.line_number - 1

        if position == "before":
            insert_at = tgt_line_adj
        elif position == "after":
            tgt_end = _section_end(flat, target_idx, len(lines)) - removed_count
            insert_at = tgt_end
        else:
            insert_at = tgt_line_adj + 1

        result_lines = remaining[:insert_at] + source_lines + remaining[insert_at:]
        return "\n".join(result_lines)



def _section_end(flat: list[OutlineNode], idx: int, total_lines: int) -> int:
    current = flat[idx]
    for i in range(idx + 1, len(flat)):
        if flat[i].level <= current.level:
            return flat[i].line_number - 1
    return total_lines
