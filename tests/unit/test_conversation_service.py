import pytest
from src.logic.conversation_service import ConversationService, ChatMessage


def test_conversation_empty():
    conv = ConversationService()
    assert conv.messages == []
    assert conv.is_waiting is False
    assert conv.last_assistant_message is None


def test_add_user_message():
    conv = ConversationService()
    msg = conv.add_user_message("Hello", context_mode="none")
    assert msg.role == "user"
    assert msg.content == "Hello"
    assert msg.context_mode == "none"
    assert msg.id is not None
    assert msg.timestamp is not None
    assert conv.is_waiting is True
    assert len(conv.messages) == 1


def test_add_assistant_message():
    conv = ConversationService()
    conv.add_user_message("Hello")
    msg = conv.add_assistant_message("Hi there")
    assert msg.role == "assistant"
    assert msg.content == "Hi there"
    assert conv.is_waiting is False


def test_last_assistant_message():
    conv = ConversationService()
    assert conv.last_assistant_message is None
    conv.add_user_message("Q1")
    conv.add_assistant_message("A1")
    conv.add_user_message("Q2")
    conv.add_assistant_message("A2")
    assert conv.last_assistant_message.content == "A2"


def test_get_history_dicts():
    conv = ConversationService()
    conv.add_user_message("Hello", context_mode="selected_text")
    conv.add_assistant_message("World")
    dicts = conv.get_history_dicts()
    assert len(dicts) == 2
    assert dicts[0]["role"] == "user"
    assert dicts[0]["content"] == "Hello"
    assert dicts[0]["context_mode"] == "selected_text"
    assert dicts[1]["role"] == "assistant"
    assert dicts[1]["content"] == "World"
    assert dicts[1]["context_mode"] is None


def test_clear():
    conv = ConversationService()
    conv.add_user_message("Hello")
    conv.add_assistant_message("World")
    assert len(conv.messages) == 2
    conv.clear()
    assert conv.messages == []
    assert conv.is_waiting is False


def test_chat_message_to_dict():
    msg = ChatMessage("user", "test", context_mode="document")
    d = msg.to_dict()
    assert d["role"] == "user"
    assert d["content"] == "test"
    assert d["context_mode"] == "document"
    assert "id" in d
    assert "timestamp" in d


def test_chat_message_custom_id():
    msg = ChatMessage("user", "t", msg_id="custom1")
    assert msg.id == "custom1"
