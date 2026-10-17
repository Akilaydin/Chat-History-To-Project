from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Any

from .models import Conversation, Message
from .tokenizer import Counter, TokenCounter, compact_json


class SplitLimitError(ValueError):
    pass


@dataclass(frozen=True)
class _Record:
    data: dict[str, Any]
    tokens: int
    bytes: int


def split_conversations(
    conversations: Iterable[Conversation],
    *,
    max_files: int,
    max_tokens_per_file: int,
    max_bytes_per_file: int,
    counter: Counter | None = None,
) -> list[list[dict[str, Any]]]:
    if max_files <= 0:
        raise ValueError("max_files must be greater than zero")
    if max_tokens_per_file <= 0:
        raise ValueError("max_tokens_per_file must be greater than zero")
    if max_bytes_per_file <= 0:
        raise ValueError("max_bytes_per_file must be greater than zero")

    token_counter = counter or TokenCounter()
    records: list[_Record] = []
    for conversation in conversations:
        records.extend(
            _conversation_records(
                conversation,
                counter=token_counter,
                max_tokens=max_tokens_per_file,
                max_bytes=max_bytes_per_file,
            )
        )

    if not records:
        return []

    estimated_parts: list[list[_Record]] = []
    current: list[_Record] = []
    current_tokens = _array_token_overhead(token_counter)
    current_bytes = 2
    separator_tokens = token_counter.count_text(",")

    for record in records:
        extra_tokens = record.tokens + (separator_tokens if current else 0)
        extra_bytes = record.bytes + (1 if current else 0)
        if current and (
            current_tokens + extra_tokens > max_tokens_per_file
            or current_bytes + extra_bytes > max_bytes_per_file
        ):
            estimated_parts.append(current)
            current = []
            current_tokens = _array_token_overhead(token_counter)
            current_bytes = 2
            extra_tokens = record.tokens
            extra_bytes = record.bytes

        current.append(record)
        current_tokens += extra_tokens
        current_bytes += extra_bytes

    if current:
        estimated_parts.append(current)

    exact_parts: list[list[_Record]] = []
    for part in estimated_parts:
        exact_parts.extend(
            _split_part_exactly(
                part,
                counter=token_counter,
                max_tokens=max_tokens_per_file,
                max_bytes=max_bytes_per_file,
            )
        )

    if len(exact_parts) > max_files:
        raise SplitLimitError(
            f"The selected history requires {len(exact_parts)} files, but the configured limit is "
            f"{max_files}. Output order cannot be changed to fit more data. "
            "Use filters, choose a plan with a larger limit, or override --max-files."
        )

    return [[record.data for record in part] for part in exact_parts]


def _conversation_records(
    conversation: Conversation,
    *,
    counter: Counter,
    max_tokens: int,
    max_bytes: int,
) -> list[_Record]:
    whole = _measure(conversation.to_output_dict(), counter)
    if _record_fits(whole, counter, max_tokens, max_bytes):
        return [whole]

    if not conversation.messages:
        raise SplitLimitError(f"Conversation '{conversation.title}' cannot fit in a single file.")

    groups = _split_messages(conversation, counter, max_tokens, max_bytes)
    group_count = len(groups)
    records = [
        _measure(
            conversation.to_output_dict(
                messages=group,
                fragment_index=index,
                fragment_count=group_count,
            ),
            counter,
        )
        for index, group in enumerate(groups, start=1)
    ]

    for record in records:
        if not _record_fits(record, counter, max_tokens, max_bytes):
            raise SplitLimitError(
                "A fragment of conversation "
                f"'{conversation.title}' still exceeds the per-file limit."
            )
    return records


def _split_messages(
    conversation: Conversation,
    counter: Counter,
    max_tokens: int,
    max_bytes: int,
) -> list[tuple[Message, ...]]:
    groups: list[tuple[Message, ...]] = []
    current: list[Message] = []

    for message in conversation.messages:
        candidate = tuple([*current, message])
        measured = _measure(
            conversation.to_output_dict(
                messages=candidate,
                fragment_index=9999,
                fragment_count=9999,
            ),
            counter,
        )

        if current and not _record_fits(measured, counter, max_tokens, max_bytes):
            groups.append(tuple(current))
            current = [message]
            single = _measure(
                conversation.to_output_dict(
                    messages=(message,),
                    fragment_index=9999,
                    fragment_count=9999,
                ),
                counter,
            )
            if not _record_fits(single, counter, max_tokens, max_bytes):
                raise SplitLimitError(
                    "A single message in conversation "
                    f"'{conversation.title}' exceeds the per-file limit."
                )
        else:
            current.append(message)

    if current:
        groups.append(tuple(current))
    return groups


def _measure(data: dict[str, Any], counter: Counter) -> _Record:
    serialized = compact_json(data)
    return _Record(
        data=data,
        tokens=counter.count_text(serialized),
        bytes=len(serialized.encode("utf-8")),
    )


def _split_part_exactly(
    records: list[_Record],
    *,
    counter: Counter,
    max_tokens: int,
    max_bytes: int,
) -> list[list[_Record]]:
    if _payload_fits(records, counter, max_tokens, max_bytes):
        return [records]

    result: list[list[_Record]] = []
    remaining = records
    while remaining:
        low = 1
        high = len(remaining)
        best = 0

        while low <= high:
            middle = (low + high) // 2
            candidate = remaining[:middle]
            if _payload_fits(candidate, counter, max_tokens, max_bytes):
                best = middle
                low = middle + 1
            else:
                high = middle - 1

        if best == 0:
            raise SplitLimitError("A single output record exceeds the configured per-file limit.")

        result.append(remaining[:best])
        remaining = remaining[best:]

    return result


def _payload_fits(
    records: list[_Record],
    counter: Counter,
    max_tokens: int,
    max_bytes: int,
) -> bool:
    serialized = compact_json([record.data for record in records])
    return (
        counter.count_text(serialized) <= max_tokens
        and len(serialized.encode("utf-8")) <= max_bytes
    )


def _record_fits(
    record: _Record,
    counter: Counter,
    max_tokens: int,
    max_bytes: int,
) -> bool:
    return (
        record.tokens + _array_token_overhead(counter) <= max_tokens
        and record.bytes + 2 <= max_bytes
    )


def _array_token_overhead(counter: Counter) -> int:
    # Packing uses independently measured records for speed. The finished payload
    # is re-tokenized exactly before it is returned.
    return counter.count_text("[]")
