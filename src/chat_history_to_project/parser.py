from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .models import Conversation, Message


def parse_conversations(raw_chats: list[dict[str, Any]]) -> list[Conversation]:
    parsed = []
    for chat in raw_chats:
        conversation = parse_conversation(chat)
        if conversation is not None:
            parsed.append(conversation)
    return parsed


def parse_conversation(chat: dict[str, Any]) -> Conversation | None:
    if not chat:
        return None

    messages: list[Message] = []
    for value in _visible_mapping_nodes(chat):
        message = value.get("message")
        if not message or not message.get("content"):
            continue

        content = message["content"]
        parts = _content_parts(content)
        if not parts:
            continue

        messages.append(
            Message(
                role=message["author"]["role"],
                content=parts,
                create_time=_parse_timestamp(message.get("create_time")),
            )
        )

    return Conversation(
        title=chat["title"],
        messages=tuple(messages),
        create_time=_conversation_timestamp(chat, messages),
    )


def _visible_mapping_nodes(
    chat: dict[str, Any],
) -> list[dict[str, Any]]:
    mapping = chat["mapping"]
    current_node = chat.get("current_node")
    if not current_node or current_node not in mapping:
        return list(mapping.values())

    visible_keys: list[str] = []
    seen: set[str] = set()
    node_key: str | None = current_node
    while node_key is not None and node_key in mapping and node_key not in seen:
        visible_keys.append(node_key)
        seen.add(node_key)
        node_key = mapping[node_key].get("parent")

    visible_keys.reverse()
    return [mapping[key] for key in visible_keys]


def _content_parts(content: dict[str, Any]) -> tuple[Any, ...]:
    if "parts" in content:
        return tuple(content.get("parts") or [])
    if "text" in content:
        return (content["text"],)
    return ()


def _conversation_timestamp(chat: dict[str, Any], messages: list[Message]) -> datetime | None:
    top_level = _parse_timestamp(chat.get("create_time"))
    if top_level is not None:
        return top_level
    return next(
        (message.create_time for message in messages if message.create_time is not None),
        None,
    )


def _parse_timestamp(value: Any) -> datetime | None:
    if value is None:
        return None
    timestamp = float(value)
    if abs(timestamp) >= 100_000_000_000:
        # Official exports can contain millisecond epoch timestamps.
        timestamp /= 1000
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)
