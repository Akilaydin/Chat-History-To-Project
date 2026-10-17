from __future__ import annotations

from collections.abc import Iterable
from datetime import date

from .models import Conversation


def filter_conversations(
    conversations: Iterable[Conversation],
    *,
    from_date: date | None = None,
    to_date: date | None = None,
    include: tuple[str, ...] = (),
    exclude: tuple[str, ...] = (),
) -> list[Conversation]:
    return [
        conversation
        for conversation in conversations
        if matches_conversation(
            conversation,
            from_date=from_date,
            to_date=to_date,
            include=include,
            exclude=exclude,
        )
    ]


def matches_conversation(
    conversation: Conversation,
    *,
    from_date: date | None = None,
    to_date: date | None = None,
    include: tuple[str, ...] = (),
    exclude: tuple[str, ...] = (),
) -> bool:
    include_terms = tuple(term.casefold() for term in include)
    exclude_terms = tuple(term.casefold() for term in exclude)
    if from_date is not None or to_date is not None:
        if conversation.create_time is None:
            return False
        conversation_date = conversation.create_time.date()
        if from_date is not None and conversation_date < from_date:
            return False
        if to_date is not None and conversation_date > to_date:
            return False

    if not include_terms and not exclude_terms:
        return True

    searchable = conversation.searchable_text().casefold()
    if include_terms and not any(term in searchable for term in include_terms):
        return False
    if exclude_terms and any(term in searchable for term in exclude_terms):
        return False
    return True
