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

            # Count leading # characters
            level = 0
            for ch in stripped:
                if ch == "#":
                    level += 1
                else:
                    break

            if level < 1 or level > 6:
                continue

            # Must have a space after the # markers
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
