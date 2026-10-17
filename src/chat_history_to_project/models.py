from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class Message:
    role: str
    content: tuple[Any, ...]
    create_time: datetime | None = None

    def to_output_dict(self) -> dict[str, Any]:
        # A single text part is represented directly as a string. Multimodal
        # content and multiple parts keep their original order and structure.
        content: Any = (
            self.content[0]
            if len(self.content) == 1 and isinstance(self.content[0], str)
            else list(self.content)
        )
        return {
            "role": self.role,
            "content": content,
        }

    def searchable_text(self) -> str:
        return json.dumps(self.content, ensure_ascii=False)


@dataclass(frozen=True)
class Conversation:
    title: str
    messages: tuple[Message, ...]
    create_time: datetime | None = None

    def to_output_dict(
        self,
        messages: tuple[Message, ...] | None = None,
        fragment_index: int | None = None,
        fragment_count: int | None = None,
    ) -> dict[str, Any]:
        selected_messages = self.messages if messages is None else messages
        title = self.title
        if fragment_index is not None and fragment_count is not None:
            title = f"{title} (part {fragment_index}/{fragment_count})"

        return {
            "title": title,
            "messages": [message.to_output_dict() for message in selected_messages],
        }

    def searchable_text(self) -> str:
        return "\n".join([self.title, *(message.searchable_text() for message in self.messages)])
