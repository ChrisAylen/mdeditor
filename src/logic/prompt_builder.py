SYSTEM_PROMPT = (
    "You are assisting with editing a markdown document. "
    "Preserve markdown formatting where appropriate. "
    "Return markdown-compatible output. "
    "Avoid unnecessary commentary when rewriting text. "
    "Keep code blocks intact unless asked to change them."
)


class PromptBuilder:
    CONTEXT_SELECTED = "selected_text"
    CONTEXT_DOCUMENT = "document"
    CONTEXT_NONE = "none"

    @staticmethod
    def build(
        user_prompt: str,
        context_mode: str,
        selected_text: str | None,
        full_document: str | None,
        history: list[dict] | None = None,
    ) -> str:
        parts = [f"System: {SYSTEM_PROMPT}"]

        if context_mode == PromptBuilder.CONTEXT_SELECTED and selected_text:
            parts.append("Context mode: Selected Text")
            parts.append(f"Selected text:\n---\n{selected_text}\n---")
        elif context_mode == PromptBuilder.CONTEXT_DOCUMENT and full_document:
            parts.append("Context mode: Current Document")
            trunc = full_document
            if len(trunc) > 12000:
                trunc = trunc[:12000] + "\n...[truncated]"
            parts.append(f"Current document:\n---\n{trunc}\n---")
        else:
            parts.append("Context mode: None")

        history = history or []
        if history:
            conv = ["Previous conversation:"]
            for msg in history:
                role = msg["role"].capitalize()
                conv.append(f"\n{role}:\n{msg['content']}")
            parts.append("".join(conv))

        parts.append(f"User request:\n{user_prompt}")
        return "\n\n".join(parts)
