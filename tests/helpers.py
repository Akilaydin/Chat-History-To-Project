from __future__ import annotations

from datetime import datetime, timezone

from chat_history_to_project.models import Conversation, Message


class CharacterCounter:
    def count_text(self, text: str) -> int:
        return len(text)


def conversation(title: str, *contents: str, create_time: datetime | None = None) -> Conversation:
    messages = tuple(
        Message(
            role="user" if index % 2 == 0 else "assistant",
            content=(content,),
            create_time=create_time,
        )
        for index, content in enumerate(contents)
    )
    return Conversation(
        title=title,
        messages=messages,
        create_time=create_time or datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


def raw_chat(title: str, content: str, create_time: float = 1_767_225_600.0) -> dict:
    return {
        "title": title,
        "create_time": create_time,
        "mapping": {
            "1": {
                "id": "1",
                "parent": None,
                "children": [],
                "message": {
                    "author": {"role": "user"},
                    "content": {"parts": [content]},
                    "create_time": create_time,
                },
            }
        },
    }
