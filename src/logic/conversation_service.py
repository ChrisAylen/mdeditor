import uuid
from datetime import datetime


class ChatMessage:
    def __init__(
        self,
        role: str,
        content: str,
        context_mode: str | None = None,
        msg_id: str | None = None,
        timestamp: str | None = None,
    ):
        self.id = msg_id or uuid.uuid4().hex[:8]
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.utcnow().isoformat()
        self.context_mode = context_mode

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "context_mode": self.context_mode,
        }


class ConversationService:
    def __init__(self):
        self._messages: list[ChatMessage] = []
        self._is_waiting = False

    @property
    def messages(self) -> list[ChatMessage]:
        return list(self._messages)

    @property
    def is_waiting(self) -> bool:
        return self._is_waiting

    @property
    def last_assistant_message(self) -> ChatMessage | None:
        for msg in reversed(self._messages):
            if msg.role == "assistant":
                return msg
        return None

    def add_user_message(
        self, content: str, context_mode: str | None = None
    ) -> ChatMessage:
        msg = ChatMessage("user", content, context_mode=context_mode)
        self._messages.append(msg)
        self._is_waiting = True
        return msg

    def add_assistant_message(self, content: str) -> ChatMessage:
        msg = ChatMessage("assistant", content)
        self._messages.append(msg)
        self._is_waiting = False
        return msg

    def get_history_dicts(self) -> list[dict]:
        return [m.to_dict() for m in self._messages]

    def clear(self):
        self._messages.clear()
        self._is_waiting = False
