import pytest
from src.logic.outline_state import OutlineState
from src.services.markdown_parser_service import MarkdownParserService


def _make_state(md: str) -> OutlineState:
    tree = MarkdownParserService.parse_headings(md)
    state = OutlineState()
    state.update_tree(tree)
    return state


def test_update_tree_clears_active():
    state = _make_state("# A\n## B\n")
    state.active_heading_line = 1
    state.update_tree(MarkdownParserService.parse_headings(""))
    assert state.active_heading_line is None


def test_active_heading_by_line():
    state = _make_state("# Intro\n\nSome text\n\n## Details\n\nMore text\n\n### Deep\n")
    state.set_active_by_line(1)
    assert state.active_heading_line is not None
    assert state.active_heading_line == 1

    state.set_active_by_line(3)
    assert state.active_heading_line == 1

    state.set_active_by_line(5)
    assert state.active_heading_line == 5

    state.set_active_by_line(9)
    assert state.active_heading_line == 9


def test_active_returns_none_when_no_headings():
    state = _make_state("")
    state.set_active_by_line(1)
    assert state.active_heading_line is None


def test_active_after_last_heading():
    state = _make_state("# Only")
    state.set_active_by_line(100)
    assert state.active_heading_line == 1


def test_active_before_first_heading():
    state = _make_state("\n\n# Later")
    state.set_active_by_line(1)
    assert state.active_heading_line is None


def test_select_then_active_unchanged():
    state = _make_state("# A\n## B\n")
    state.set_active_by_line(1)
    active_line = state.active_heading_line
    state.select(42)
    assert state.selected_heading_line == 42
    assert state.active_heading_line == active_line


def test_select_none():
    state = _make_state("# A\n")
    state.select(42)
    state.select(None)
    assert state.selected_heading_line is None
