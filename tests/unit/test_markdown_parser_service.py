import pytest
from src.services.markdown_parser_service import MarkdownParserService, OutlineNode


def _find_by_title(nodes: list[OutlineNode], title: str) -> OutlineNode | None:
    for node in nodes:
        if node.title == title:
            return node
        child = _find_by_title(node.children, title)
        if child:
            return child
    return None


def test_extract_single_h1():
    tree = MarkdownParserService.parse_headings("# Hello")
    assert len(tree) == 1
    assert tree[0].title == "Hello"
    assert tree[0].level == 1


def _count_all_nodes(nodes: list[OutlineNode]) -> int:
    count = 0
    for node in nodes:
        count += 1
        count += _count_all_nodes(node.children)
    return count

def _all_nodes_flat(nodes: list[OutlineNode]) -> list[OutlineNode]:
    result = []
    for node in nodes:
        result.append(node)
        result.extend(_all_nodes_flat(node.children))
    return result

def test_extract_all_levels():
    md = "\n".join([f"{'#' * n} Heading {n}" for n in range(1, 7)])
    tree = MarkdownParserService.parse_headings(md)
    all_nodes = _all_nodes_flat(tree)
    assert len(all_nodes) == 6


def test_extract_headings_flat():
    md = "# A\n## B\n### C\n"
    flat = MarkdownParserService.extract_headings_flat(md)
    assert len(flat) == 3
    assert flat[0].title == "A"
    assert flat[1].title == "B"
    assert flat[2].title == "C"


def test_move_section_before():
    md = "# A\naaa\n## B\nbbb\n# C\nccc\n"
    flat = MarkdownParserService.extract_headings_flat(md)
    result = MarkdownParserService.move_section(md, flat, flat[1].id, flat[2].id, "before")
    assert result == md


def test_move_section_after():
    md = "# A\naaa\n## B\nbbb\n# C\nccc\n"
    flat = MarkdownParserService.extract_headings_flat(md)
    result = MarkdownParserService.move_section(md, flat, flat[1].id, flat[0].id, "after")
    lines = result.split("\n")
    assert lines[0] == "# A"
    assert lines[1] == "aaa"
    assert lines[2] == "## B"
    assert lines[3] == "bbb"
    assert lines[4] == "# C"


def test_move_section_child():
    md = "# A\naaa\n## B\nbbb"
    flat = MarkdownParserService.extract_headings_flat(md)
    result = MarkdownParserService.move_section(md, flat, flat[1].id, flat[0].id, "child")
    lines = result.split("\n")
    assert lines[0] == "# A"
    assert lines[1] == "### B"
    assert lines[2] == "bbb"
    assert lines[3] == "aaa"


def test_move_section_self_noop():
    md = "# A\n## B\n"
    flat = MarkdownParserService.extract_headings_flat(md)
    result = MarkdownParserService.move_section(md, flat, flat[0].id, flat[0].id, "after")
    assert result == md


def test_move_section_invalid_id_noop():
    md = "# A\n"
    result = MarkdownParserService.move_section(md, [], "nonexistent", "also_fake", "after")
    assert result == md


def test_headings_inside_nested_fences():
    md = """# Outside

```python
# Inside fence 1
## Also inside
```

~~~
# Inside tilde fence
~~~

## Still outside
"""
    tree = MarkdownParserService.parse_headings(md)
    all_nodes = _all_nodes_flat(tree)
    titles = [n.title for n in all_nodes]
    assert titles == ["Outside", "Still outside"]


def test_no_space_after_hash_is_not_heading():
    md = "#Not a heading\n##AlsoNot"
    tree = MarkdownParserService.parse_headings(md)
    assert len(tree) == 0


def test_empty_title_is_skipped():
    md = "# \n## "
    tree = MarkdownParserService.parse_headings(md)
    assert len(tree) == 0


def test_too_many_hashes_is_not_heading():
    md = "######## too many"
    tree = MarkdownParserService.parse_headings(md)
    assert len(tree) == 0


def test_heading_with_special_chars():
    md = "# My C++ Code\n## foo_bar()\n### $pecial!"
    tree = MarkdownParserService.parse_headings(md)
    all_nodes = _all_nodes_flat(tree)
    assert len(all_nodes) == 3


def test_no_headings_returns_empty():
    assert MarkdownParserService.parse_headings("Just plain text\n\nNo headings here") == []


def test_empty_string():
    assert MarkdownParserService.parse_headings("") == []


def test_hierarchical_tree():
    md = """# A
## B
### C
## D
# E
"""
    tree = MarkdownParserService.parse_headings(md)
    assert len(tree) == 2
    assert tree[0].title == "A"
    assert tree[1].title == "E"

    # A has children B (and B has child C) and D
    assert len(tree[0].children) == 2
    assert tree[0].children[0].title == "B"
    assert tree[0].children[1].title == "D"
    assert len(tree[0].children[0].children) == 1
    assert tree[0].children[0].children[0].title == "C"


def test_line_numbers():
    md = "# First\n\nSome text\n\n## Second\n\n### Third\n"
    tree = MarkdownParserService.parse_headings(md)
    assert tree[0].line_number == 1
    assert tree[0].children[0].line_number == 5
    assert tree[0].children[0].children[0].line_number == 7


def test_heading_with_trailing_hashes():
    md = "# Title # trailing ###"
    tree = MarkdownParserService.parse_headings(md)
    assert len(tree) == 1
    assert tree[0].title == "Title # trailing ###"


def test_unclosed_fence_still_ignores():
    md = """# Outside

```python
# Inside unclosed fence
## Still inside
"""
    tree = MarkdownParserService.parse_headings(md)
    assert len(tree) == 1
    assert tree[0].title == "Outside"


def test_fenced_code_with_tilde():
    md = """# Real

~~~
# Not real
~~~

## Real too
"""
    tree = MarkdownParserService.parse_headings(md)
    all_nodes = _all_nodes_flat(tree)
    assert len(all_nodes) == 2
