import pytest
from src.logic.prompt_builder import PromptBuilder, SYSTEM_PROMPT


def test_build_no_context():
    prompt = PromptBuilder.build("Hello", PromptBuilder.CONTEXT_NONE, None, None)
    assert SYSTEM_PROMPT in prompt
    assert "Context mode: None" in prompt
    assert "User request:\nHello" in prompt


def test_build_selected_text():
    prompt = PromptBuilder.build(
        "Summarise this", PromptBuilder.CONTEXT_SELECTED,
        "Some selected text", None,
    )
    assert "Context mode: Selected Text" in prompt
    assert "Some selected text" in prompt
    assert "User request:\nSummarise this" in prompt


def test_build_selected_text_empty_fallback():
    prompt = PromptBuilder.build(
        "Hello", PromptBuilder.CONTEXT_SELECTED, None, None,
    )
    assert "Context mode: None" in prompt
    assert "Selected text" not in prompt


def test_build_document():
    prompt = PromptBuilder.build(
        "Review this", PromptBuilder.CONTEXT_DOCUMENT,
        None, "Full doc content here",
    )
    assert "Context mode: Current Document" in prompt
    assert "Full doc content here" in prompt
    assert "User request:\nReview this" in prompt


def test_build_document_empty_fallback():
    prompt = PromptBuilder.build(
        "Hello", PromptBuilder.CONTEXT_DOCUMENT, None, None,
    )
    assert "Context mode: None" in prompt
    assert "Current document" not in prompt


def test_build_truncates_large_document():
    large = "x" * 20000
    prompt = PromptBuilder.build(
        "Hi", PromptBuilder.CONTEXT_DOCUMENT, None, large,
    )
    assert "...[truncated]" in prompt
    assert len(prompt) < 15000


def test_build_with_history():
    history = [
        {"role": "user", "content": "What is this?"},
        {"role": "assistant", "content": "A markdown file."},
    ]
    prompt = PromptBuilder.build(
        "Expand", PromptBuilder.CONTEXT_NONE, None, None, history=history,
    )
    assert "Previous conversation:" in prompt
    assert "User:\nWhat is this?" in prompt
    assert "Assistant:\nA markdown file." in prompt
    assert "User request:\nExpand" in prompt
